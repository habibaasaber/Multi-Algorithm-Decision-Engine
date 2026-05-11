// ========== BACKEND INTEGRATION ==========
const API_URL = "http://localhost:5000";

const ALGORITHMS = {
    BRUTE_FORCE: 'knapsack_brute_force', // map to backend identifiers somewhat? Or use the returned
    DYNAMIC_PROGRAMMING: 'knapsack_dp',
    DIVIDE_AND_CONQUER: 'merge_sort_dc',
    GREEDY: 'fractional_knapsack_greedy'
};

let currentResults = {
    type: null,
    n: null,
    T: null,
    quality: null,
    decision: null,
    solution: null,
    runtime_ms: null,
    experiment: null
};

async function callSolveApi(type, n, T, quality) {
    try {
        const response = await fetch(`${API_URL}/solve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_type: type,
                n: n,
                time_budget_ms: T,
                quality_requirement: quality
            })
        });
        if (!response.ok) {
            const err = await response.json();
            let errorMsg = err.detail || "API Error";
            if (typeof errorMsg === 'object') {
                errorMsg = errorMsg.error || JSON.stringify(errorMsg);
            }
            throw new Error(errorMsg);
        }
        return await response.json();
    } catch (e) {
        throw e;
    }
}

async function callCompareApi(type, n, algorithms) {
    try {
        const response = await fetch(`${API_URL}/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_type: type,
                n: n,
                runs: 1,
                algorithms: algorithms
            })
        });
        if (!response.ok) {
            const err = await response.json();
            let errorMsg = err.detail || "API Error";
            if (typeof errorMsg === 'object') {
                errorMsg = errorMsg.error || JSON.stringify(errorMsg);
            }
            throw new Error(errorMsg);
        }
        return await response.json();
    } catch (e) {
        throw e;
    }
}

async function callBenchmarkApi(type, algorithms) {
    try {
        const response = await fetch(`${API_URL}/benchmark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_type: type,
                algorithms: algorithms
            })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Benchmark API Error");
        }
        return await response.json();
    } catch (e) {
        throw e;
    }
}
async function exportPdf() {
    if (!currentResults.decision && !currentResults.experiment) {
        alert("No results to export. Please run a solve or experiment first.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/export-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                decision: currentResults.decision,
                solution: currentResults.solution,
                problem_type: currentResults.type,
                runtime_ms: currentResults.runtime_ms,
                n: currentResults.n,
                time_budget_ms: currentResults.T,
                quality_requirement: currentResults.quality
            })
        });

        if (!response.ok) throw new Error("Failed to generate PDF");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `algorithm_report_${currentResults.type}_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (e) {
        alert("Error exporting PDF: " + e.message);
    }
}

// Map backend algo classes to UI
function getAlgoClass(backendAlgoName) {
    if (backendAlgoName.includes('brute_force')) return { name: 'Brute Force', css: 'brute-force' };
    if (backendAlgoName.includes('dp')) return { name: 'Dynamic Programming', css: 'dp' };
    if (backendAlgoName.includes('dc')) return { name: 'Divide and Conquer', css: 'divide-conquer' };
    if (backendAlgoName.includes('greedy')) return { name: 'Greedy', css: 'greedy' };
    return { name: backendAlgoName, css: 'dp' };
}

function getComplexityMetrics(algorithmName) {
    const registry = {
        'knapsack_dp': { time: "O(n × W)", space: "O(n × W)", quality: "100% Optimal" },
        'sequence_alignment_dp': { time: "O(n × m)", space: "O(n × m)", quality: "100% Optimal" },
        'bellman_ford_dp': { time: "O(V × E)", space: "O(V)", quality: "100% Optimal" },
        'weighted_interval_scheduling_dp': { time: "O(n log n)", space: "O(n)", quality: "100% Optimal" },
        'fractional_knapsack_greedy': { time: "O(n log n)", space: "O(n)", quality: "100% Optimal" },
        'kruskal_mst_greedy': { time: "O(E log E)", space: "O(V + E)", quality: "100% Optimal" },
        'dijkstra_greedy': { time: "O(V²)", space: "O(V)", quality: "100% Optimal" },
        'merge_sort_dc': { time: "O(n log n)", space: "O(n)", quality: "100% Optimal" },
        'binary_search_dc': { time: "O(log n)", space: "O(1)", quality: "100% Optimal" },
        'fast_exponentiation_dc': { time: "O(log n)", space: "O(log n)", quality: "100% Optimal" },
        'knapsack_brute_force': { time: "O(2^n)", space: "O(2^n)", quality: "100% Optimal" },
        'subset_bruteforce': { time: "O(2^n)", space: "O(2^n)", quality: "100% Optimal" },
        'matrix_multiplication_dc': { time: "O(n^log₂7)", space: "O(n²)", quality: "100% Optimal" }
    };
    return registry[algorithmName] || { time: "O(?)", space: "O(?)", quality: "Unknown" };
}

// ========== UI GENERATION ==========

function renderRecommendation(decision, type, n, T, quality) {
    const container = document.getElementById('recommendationContainer');
    
    if (!decision) {
        container.innerHTML = `<div class="loading-container"><div class="spinner"></div>Analyzing problem space...</div>`;
        return;
    }
    
    const backendAlgoName = decision.algorithm_name;
    const algoInfo = getAlgoClass(backendAlgoName);
    const metrics = getComplexityMetrics(backendAlgoName);

    let timeComplexity = metrics.time;
    let spaceComplexity = metrics.space;
    let qualityGuarantee = metrics.quality;
    let approxRatio = decision.approx_ratio || 1.0;
    let justification = decision.justification || "Algorithm chosen by Decision Engine.";

    const warningBox = backendAlgoName.includes('brute_force') ? 
        `<div class="warning-box">⚠ WARNING: Brute Force is infeasible for n > 15. Use only for correctness verification.</div>` :
        (backendAlgoName.includes('greedy') && !['fractional_knapsack', 'mst'].includes(type) ?
        `<div class="warning-box amber">⚠ Greedy may not be within a known bound of optimal for this problem type.</div>` : '');

    const html = `
        <div class="recommendation-card">
            <div class="algorithm-badge ${algoInfo.css}">${algoInfo.name}</div>
            <p class="recommendation-text">${justification}</p>
            <div class="metrics-chips">
                <div class="metric-chip">
                    <span class="metric-chip-label">⏱ Time</span>
                    <span class="metric-chip-value">${timeComplexity}</span>
                </div>
                <div class="metric-chip">
                    <span class="metric-chip-label">💾 Space</span>
                    <span class="metric-chip-value">${spaceComplexity}</span>
                </div>
                <div class="metric-chip">
                    <span class="metric-chip-label">✅ Quality</span>
                    <span class="metric-chip-value">${qualityGuarantee}</span>
                </div>
                <div class="metric-chip">
                    <span class="metric-chip-label">⚖ Ratio</span>
                    <span class="metric-chip-value">${(approxRatio * 100).toFixed(0)}%</span>
                </div>
            </div>
            ${warningBox}
        </div>
    `;

    container.innerHTML = html;
}

function renderSolutionData(resultObj, type) {
    const solution = resultObj.solution;
    const container = document.getElementById('solutionContainer');
    
    let solutionHTML = '<div class="solution-card">';
    solutionHTML += `<div class="solution-title">Solution Results</div><div class="solution-content">`;
    
    try {
        if (type === 'knapsack' || type === 'fractional_knapsack') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Optimal Value</span>
                <span class="result-row-value">${solution.max_value !== undefined ? solution.max_value : (solution.total_value !== undefined ? solution.total_value : 'N/A')}</span>
            </div>`;
            
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;

            if (type === 'fractional_knapsack' && solution.fractions) {
                solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Fractional Selection</span></div>';
                solutionHTML += '<div class="dp-table-container"><table class="dp-table"><thead><tr><td class="header">Item Index</td><td class="header">Fraction Taken</td></tr></thead><tbody>';
                solution.fractions.forEach((f, idx) => {
                    if (f > 0) {
                        solutionHTML += `<tr><td>${idx}</td><td class="${f === 1.0 ? 'optimal' : 'path'}">${(f * 100).toFixed(1)}%</td></tr>`;
                    }
                });
                solutionHTML += '</tbody></table></div>';
            }
            
            if (solution.selected_items) {
                solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Selected Items</span></div>';
                solutionHTML += '<div class="items-list">';
                if (Array.isArray(solution.selected_items)) {
                    solution.selected_items.forEach((item, idx) => {
                        let id = typeof item === 'object' ? item.id : item;
                        solutionHTML += `<div class="item-chip">Item ${id}</div>`;
                    });
                }
                solutionHTML += '</div>';
            }
        } 
        else if (type === 'mst') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">MST Total Weight</span>
                <span class="result-row-value">${solution.total_weight}</span>
            </div>`;
            
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
            
            if (solution.mst_edges) {
                solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">MST Edges</span></div>';
                solutionHTML += '<div class="items-list">';
                solution.mst_edges.forEach(edge => {
                    let from = edge.from !== undefined ? edge.from : edge[0];
                    let to = edge.to !== undefined ? edge.to : edge[1];
                    let w = edge.weight !== undefined ? edge.weight : edge[2];
                    solutionHTML += `<div class="item-chip">${from}→${to}<div class="item-chip-value">w=${w}</div></div>`;
                });
                solutionHTML += '</div>';
            }
        }
        else if (type === 'sorting') {
            solutionHTML += `<div class="result-row" style="margin-top: 12px;">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
            
            if (solution.sorted_array) {
                solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Sorted Array Snippet</span></div>';
                solutionHTML += '<div class="array-display">';
                let arr = solution.sorted_array.slice(0, 20); // show up to 20
                arr.forEach(num => {
                    solutionHTML += `<div class="number-chip sorted">${num}</div>`;
                });
                if (solution.sorted_array.length > 20) {
                    solutionHTML += `<div class="number-chip">...</div>`;
                }
                solutionHTML += '</div>';
            }
        }
        else if (type === 'sequence_alignment') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Alignment Score</span>
                <span class="result-row-value">${solution.score || '?'}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Sequence 1</span>
                <span class="result-row-value" style="font-family: 'JetBrains Mono', monospace;">${solution.aligned_a || ''}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Sequence 2</span>
                <span class="result-row-value" style="font-family: 'JetBrains Mono', monospace;">${solution.aligned_b || ''}</span>
            </div>`;
            
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
        }
        else if (type === 'matrix_mult') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Dimension</span>
                <span class="result-row-value">${solution.n} x ${solution.n}</span>
            </div>`;
            
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
            if (solution.result_matrix) {
                solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Product Matrix Snippet (3x3)</span></div>';
                solutionHTML += '<div class="dp-table-container"><table class="dp-table">';
                solution.result_matrix.slice(0, 3).forEach(row => {
                    solutionHTML += '<tr>';
                    row.slice(0, 3).forEach(val => {
                        solutionHTML += `<td>${val}</td>`;
                    });
                    if (row.length > 3) solutionHTML += '<td>...</td>';
                    solutionHTML += '</tr>';
                });
                if (solution.result_matrix.length > 3) solutionHTML += '<tr><td>...</td><td>...</td><td>...</td><td>...</td></tr>';
                solutionHTML += '</table></div>';
            }
        }
        else if (type === 'shortest_path') {
            const numNodes = solution.distances.length;
            const targetNode = numNodes - 1;
            const distance = solution.distances[targetNode];
            
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Distance to Node ${targetNode}</span>
                <span class="result-row-value">${distance !== Infinity ? distance : 'Unreachable'}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
            
            if (distance !== Infinity) {
                solutionHTML += `<div style="margin-top: 12px;"><span class="result-row-label">Shortest Path (0 → ${targetNode})</span></div>`;
                solutionHTML += '<div class="items-list">';
                
                // Reconstruct path
                let path = [];
                let curr = targetNode;
                while (curr !== -1) {
                    path.push(curr);
                    curr = solution.predecessors[curr];
                }
                path.reverse();
                
                path.forEach((node, idx) => {
                    solutionHTML += `<div class="item-chip">${node}</div>`;
                    if (idx < path.length - 1) solutionHTML += '<span style="color:var(--cyan); margin:0 4px;">→</span>';
                });
                solutionHTML += '</div>';
            }
            
            solutionHTML += `<div style="margin-top: 12px;"><span class="result-row-label">All Final Distances</span></div>`;
            solutionHTML += '<div class="items-list">';
            solution.distances.forEach((dist, idx) => {
                if (dist !== Infinity) {
                    solutionHTML += `<div class="item-chip">Node ${idx}<div class="item-chip-value">d=${dist}</div></div>`;
                }
            });
            solutionHTML += '</div>';
        }
        else if (type === 'scheduling') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Total Weight</span>
                <span class="result-row-value">${solution.max_weight}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
            if (solution.selected_intervals) {
                solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Selected Intervals</span></div>';
                solutionHTML += '<div class="items-list">';
                solution.selected_intervals.forEach(inv => {
                    solutionHTML += `<div class="item-chip">${inv[0]}-${inv[1]}<div class="item-chip-value">w=${inv[2]}</div></div>`;
                });
                solutionHTML += '</div>';
            }
        }
        else if (type === 'searching') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Target Found?</span>
                <span class="result-row-value" style="color:${solution.index !== -1 ? 'var(--emerald)' : 'var(--red)'}">${solution.index !== -1 ? 'YES (Index ' + solution.index + ')' : 'NO'}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Steps (Comparisons)</span>
                <span class="result-row-value">${solution.steps}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
        }
        else if (type === 'exponentiation') {
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Result</span>
                <span class="result-row-value">${solution.result.toString().substring(0, 15)}...</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Multiplications</span>
                <span class="result-row-value">${solution.multiplications}</span>
            </div>`;
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
        }
        else {
            // Generic output
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Raw Output</span>
                <span class="result-row-value" style="font-size:10px;">${JSON.stringify(solution).substring(0, 100)}...</span>
            </div>`;
            
            solutionHTML += `<div class="result-row">
                <span class="result-row-label">Runtime</span>
                <span class="result-row-value">${(solution.runtime_ms || resultObj.runtime_ms || 0).toFixed(4)} ms</span>
            </div>`;
        }

        if (solution.states_evaluated !== undefined) {
            solutionHTML += `<div class="result-row" style="margin-top: 12px;">
                <span class="result-row-label">States Evaluated</span>
                <span class="result-row-value" style="color:var(--amber);">${solution.states_evaluated}</span>
            </div>`;
        }

        if (solution.recursion_depth !== undefined) {
            solutionHTML += `<div class="result-row" style="margin-top: 12px;">
                <span class="result-row-label">Recursion Depth</span>
                <span class="result-row-value">${solution.recursion_depth}</span>
            </div>`;
        }

        if (solution.level_sizes && Array.isArray(solution.level_sizes)) {
            solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Sub-problem Sizes (Levels)</span></div>';
            solutionHTML += '<div class="items-list">';
            solution.level_sizes.slice(0, 8).forEach(lvl => {
                let txt = JSON.stringify(lvl).replace(/[{}"_]/g, ' ').trim();
                solutionHTML += `<div class="item-chip" style="font-size:10px;">${txt}</div>`;
            });
            if (solution.level_sizes.length > 8) solutionHTML += `<div class="item-chip">...</div>`;
            solutionHTML += '</div>';
        }

        if (solution.backtrack_sequence && Array.isArray(solution.backtrack_sequence)) {
            solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">Backtrack Sequence</span></div>';
            solutionHTML += '<div class="items-list">';
            solution.backtrack_sequence.forEach(step => {
                solutionHTML += `<div class="item-chip" style="font-size:10px;">${step}</div>`;
            });
            solutionHTML += '</div>';
        }

        if (solution.dp_table && Array.isArray(solution.dp_table)) {
            solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">DP Table Analysis</span></div>';
            solutionHTML += '<div class="dp-table-container"><table class="dp-table">';
            
            // Check if 2D or 1D
            const is2D = Array.isArray(solution.dp_table[0]);
            
            if (is2D) {
                // Render 2D Table (e.g. Knapsack, Sequence Alignment)
                solution.dp_table.slice(0, 50).forEach((row, i) => {
                    solutionHTML += '<tr>';
                    row.slice(0, 20).forEach((col, j) => {
                        solutionHTML += `<td>${typeof col === 'number' ? col.toFixed(0) : col}</td>`;
                    });
                    if (row.length > 20) solutionHTML += '<td>...</td>';
                    solutionHTML += '</tr>';
                });
            } else {
                // Render 1D Table (e.g. Scheduling)
                solutionHTML += '<tr>';
                solution.dp_table.slice(0, 50).forEach((val, i) => {
                    solutionHTML += `<td>${typeof val === 'number' ? val.toFixed(0) : val}</td>`;
                });
                if (solution.dp_table.length > 50) solutionHTML += '<td>...</td>';
                solutionHTML += '</tr>';
            }
            solutionHTML += '</table></div>';
        }

    } catch (e) {
        solutionHTML += `<div class="solution-title">Error rendering</div><p>${e.message}</p>`;
    }

    solutionHTML += '</div></div>';
    container.innerHTML = solutionHTML;
    
    setTimeout(() => {
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}


// ========== FLOWCHART GENERATION ==========
function generateFlowchart(decisionObj, type, n, T, quality) {
    const svg = document.getElementById('flowchart');
    svg.innerHTML = '';

    const viewBoxWidth = 400;
    const viewBoxHeight = 650;
    svg.setAttribute('viewBox', `0 0 ${viewBoxWidth} ${viewBoxHeight}`);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

    const backendAlgoName = decisionObj ? decisionObj.algorithm_name : '';
    
    const cx = viewBoxWidth / 2;
    const leftX = 80;
    const rightX = 320;

    const nodes = [
        { x: cx, y: 40, text: 'START', type: 'start' },                                // 0
        { x: cx, y: 120, text: `Type: ${type.toUpperCase()}`, type: 'decision' },       // 1
        { x: cx, y: 200, text: 'Subset?', type: 'decision' },                          // 2
        { x: leftX, y: 260, text: 'BRUTE FORCE', type: 'algorithm', key: 'brute_force' }, // 3
        { x: cx, y: 280, text: `n=${n} Suitable?`, type: 'decision' },                 // 4
        { x: rightX, y: 340, text: 'DYN. PROG.', type: 'algorithm', key: 'dp' },       // 5
        { x: cx, y: 360, text: 'Sort/Matrix?', type: 'decision' },                     // 6
        { x: leftX, y: 420, text: 'DIV. CONQUER', type: 'algorithm', key: 'dc' },      // 7
        { x: cx, y: 440, text: `T=${T}ms Qual=${quality}`, type: 'decision' },         // 8
        { x: rightX, y: 500, text: 'GREEDY', type: 'algorithm', key: 'greedy' },       // 9
        { x: cx, y: 600, text: 'END', type: 'end' }                                    // 10
    ];

    // Determine path based on backend name
    let pathNodes = [0, 1, 2];
    if (backendAlgoName.includes('brute_force')) {
        pathNodes.push(3, 10);
    } else if (backendAlgoName.includes('dp')) {
        pathNodes.push(4, 5, 10);
    } else if (backendAlgoName.includes('dc')) {
        pathNodes.push(4, 6, 7, 10);
    } else if (backendAlgoName.includes('greedy')) {
        pathNodes.push(4, 6, 8, 9, 10);
    } else {
        pathNodes.push(10);
    }

    const connections = [
        [0, 1], [1, 2], [2, 3, 'YES (Subset)'], [2, 4, 'NO'], [4, 5, 'YES (Small n/W)'], [4, 6, 'NO'], [6, 7, 'YES (Sort/Mat)'], [6, 8, 'NO'], [8, 9, 'YES (Fast/Approx)'], [3, 10], [5, 10], [7, 10], [9, 10]
    ];

    connections.forEach(([fromIdx, toIdx, label]) => {
        const from = nodes[fromIdx];
        const to = nodes[toIdx];
        // Ensure path connects visually correctly if active
        const isActive = pathNodes.includes(fromIdx) && pathNodes.includes(toIdx) && 
                         (pathNodes.indexOf(toIdx) === pathNodes.indexOf(fromIdx) + 1);
        drawLine(svg, from, to, isActive, label);
    });

    nodes.forEach((node, idx) => {
        const isActive = pathNodes.includes(idx);
        drawNode(svg, node, isActive);
    });
}

function drawLine(svg, from, to, active, label) {
    let x1 = from.x;
    let y1 = from.y;
    let x2 = to.x;
    let y2 = to.y;
    
    if (from.type === 'decision') {
        if (to.x < from.x) { // going left
            x1 = from.x - 55;
            y1 = from.y;
        } else if (to.x > from.x) { // going right
            x1 = from.x + 55;
            y1 = from.y;
        } else { // going down
            y1 = from.y + 30;
        }
    } else {
        y1 = from.y + 20; // box bottom
    }
    
    if (to.type === 'decision') {
        y2 = to.y - 30;
    } else {
        y2 = to.y - 20; // box top
    }
    
    // Elbow connection for decisions
    if (x1 !== x2 && from.type === 'decision') {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', `M ${x1} ${y1} L ${x2} ${y1} L ${x2} ${y2}`);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', active ? 'var(--cyan)' : 'rgba(0, 212, 255, 0.2)');
        path.setAttribute('stroke-width', active ? '2' : '1');
        path.setAttribute('stroke-dasharray', active ? '5,5' : 'none');
        if (active) path.style.animation = 'dash 20s linear infinite';
        svg.appendChild(path);

        if (label) {
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x1 + (x2-x1)/2);
            text.setAttribute('y', y1 - 10);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', active ? 'var(--cyan)' : 'var(--gray-muted)');
            text.setAttribute('font-size', '9');
            text.setAttribute('font-family', 'JetBrains Mono');
            text.textContent = label;
            svg.appendChild(text);
        }
        return;
    }

    // Elbow connection returning to END
    if (x1 !== x2 && from.type !== 'decision') {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const midY = y1 + (y2 - y1) / 2;
        path.setAttribute('d', `M ${x1} ${y1} L ${x1} ${midY} L ${x2} ${midY} L ${x2} ${y2}`);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', active ? 'var(--cyan)' : 'rgba(0, 212, 255, 0.2)');
        path.setAttribute('stroke-width', active ? '2' : '1');
        path.setAttribute('stroke-dasharray', active ? '5,5' : 'none');
        if (active) path.style.animation = 'dash 20s linear infinite';
        svg.appendChild(path);
        return;
    }

    // Straight line
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('stroke', active ? 'var(--cyan)' : 'rgba(0, 212, 255, 0.2)');
    line.setAttribute('stroke-width', active ? '2' : '1');
    line.setAttribute('stroke-dasharray', active ? '5,5' : 'none');
    if (active) line.style.animation = 'dash 20s linear infinite';
    svg.appendChild(line);

    if (label && from.type === 'decision') {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x1 + 10);
        text.setAttribute('y', y1 + 25);
        text.setAttribute('fill', active ? 'var(--cyan)' : 'var(--gray-muted)');
        text.setAttribute('font-size', '9');
        text.setAttribute('font-family', 'JetBrains Mono');
        text.textContent = label;
        svg.appendChild(text);
    }
}

function drawNode(svg, node, active) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

    if (node.type === 'decision') {
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', `${node.x},${node.y - 30} ${node.x + 55},${node.y} ${node.x},${node.y + 30} ${node.x - 55},${node.y}`);
        polygon.setAttribute('fill', active ? 'rgba(0, 212, 255, 0.2)' : 'rgba(0, 212, 255, 0.05)');
        polygon.setAttribute('stroke', active ? 'var(--cyan)' : 'rgba(0, 212, 255, 0.3)');
        polygon.setAttribute('stroke-width', '1');
        g.appendChild(polygon);
    } else {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', node.x - 45);
        rect.setAttribute('y', node.y - 20);
        rect.setAttribute('width', '90');
        rect.setAttribute('height', '40');
        rect.setAttribute('rx', '6');
        rect.setAttribute('fill', active ? 'rgba(0, 212, 255, 0.3)' : 'rgba(0, 212, 255, 0.05)');
        rect.setAttribute('stroke', active ? 'var(--cyan)' : 'rgba(0, 212, 255, 0.2)');
        rect.setAttribute('stroke-width', active ? '2' : '1');
        g.appendChild(rect);
    }

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', node.x);
    text.setAttribute('y', node.y);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dominant-baseline', 'middle');
    text.setAttribute('fill', active ? 'var(--cyan)' : 'var(--gray-text)');
    text.setAttribute('font-size', '11');
    text.setAttribute('font-family', 'JetBrains Mono, monospace');
    text.setAttribute('font-weight', active ? '700' : '400');
    text.textContent = node.text;
    g.appendChild(text);

    svg.appendChild(g);
}

// ========== EXPERIMENT MODE ==========

async function runExperiment(type, n, T, quality) {
    const experimentSection = document.getElementById('experimentSection');
    const experimentResults = document.getElementById('experimentResults');

    experimentResults.innerHTML = '<div class="loading-container"><div class="spinner"></div>Running all algorithms...</div>';
    experimentSection.classList.add('active');

    // List applicable algos based on type (only algorithms that exist in backend)
    let algorithmsToRun = [];
    if (type === 'knapsack') algorithmsToRun = ['knapsack_dp', 'knapsack_brute_force', 'fractional_knapsack_greedy'];
    else if (type === 'fractional_knapsack') algorithmsToRun = ['fractional_knapsack_greedy', 'knapsack_dp'];
    else if (type === 'subset') algorithmsToRun = ['subset_bruteforce'];
    else if (type === 'mst') algorithmsToRun = ['kruskal_mst_greedy'];
    else if (type === 'sorting') algorithmsToRun = ['merge_sort_dc'];
    else if (type === 'sequence_alignment') algorithmsToRun = ['sequence_alignment_dp'];
    else if (type === 'shortest_path') algorithmsToRun = ['dijkstra_greedy', 'bellman_ford_dp'];
    else if (type === 'scheduling') algorithmsToRun = ['weighted_interval_scheduling_dp'];
    else if (type === 'searching') algorithmsToRun = ['binary_search_dc'];
    else if (type === 'exponentiation') algorithmsToRun = ['fast_exponentiation_dc'];
    else if (type === 'matrix_mult') algorithmsToRun = ['matrix_multiplication_dc'];
    else algorithmsToRun = ['knapsack_dp']; // Fallback

    if (algorithmsToRun.length === 0) {
        experimentResults.innerHTML = `<div class="warning-box">No algorithms available for problem type: ${type}</div>`;
        return;
    }

    try {
        const compareResult = await callCompareApi(type, n, algorithmsToRun);
        const results = compareResult.comparison_results;

        if (!results || results.length === 0) {
            experimentResults.innerHTML = `<div class="warning-box">No results returned from comparison API</div>`;
            return;
        }

        // compute approximation ratios assuming best runtime or best value?
        // Wait, for comparison we need to rank by solution quality.
        // Let's assume the highest total_value or max_value is optimal.
        
        let bestFoundValue = type === 'mst' || type === 'shortest_path' ? Infinity : -Infinity;

        results.forEach(r => {
            const sol = r.latest_output;
            let val = null;
            if (sol) {
                 if (sol.max_value !== undefined) val = sol.max_value;
                 else if (sol.total_value !== undefined) val = sol.total_value;
                 else if (sol.total_weight !== undefined) val = sol.total_weight; // usually minimization
                 else if (sol.score !== undefined) val = sol.score;
                 else val = 1;
            }
            r._calculatedValue = val !== null ? val : 0;
            
            if (type === 'mst' || type === 'shortest_path') {
                if (val !== null && val < bestFoundValue) bestFoundValue = val;
            } else {
                if (val !== null && val > bestFoundValue) bestFoundValue = val;
            }
        });

        // Compute approximation ratio
        results.forEach(r => {
            if (bestFoundValue === Infinity || bestFoundValue === -Infinity || bestFoundValue === 0) {
                r.approximation = 1.0;
            } else if (type === 'mst' || type === 'shortest_path') {
                r.approximation = r._calculatedValue > 0 ? (bestFoundValue / r._calculatedValue) : 1.0; // Ratio <= 1
            } else {
                r.approximation = r._calculatedValue / bestFoundValue;
            }
        });

        // Sort descending by value (or ascending if minimization), then by runtime
        results.sort((a, b) => {
            if (type === 'mst' || type === 'shortest_path') {
                return a._calculatedValue - b._calculatedValue || a.average_runtime_ms - b.average_runtime_ms;
            } else {
                return b._calculatedValue - a._calculatedValue || a.average_runtime_ms - b.average_runtime_ms;
            }
        });

        let tableHTML = '<table class="experiment-table"><thead><tr>';
        tableHTML += '<th>Algorithm</th><th>Result Value</th><th>Runtime (ms)</th><th>Ratio</th><th>Quality</th><th>Rank</th></tr></thead><tbody>';

        results.forEach((r, idx) => {
            const algoInfo = getAlgoClass(r.algorithm);
            const rowClass = idx === 0 ? 'best' : (idx === results.length - 1 ? 'worst' : '');
            
            tableHTML += `<tr class="${rowClass}">
                <td>
                    <div style="font-weight:700; color:var(--text-white);">${algoInfo.name}</div>
                    <div style="font-size:10px; color:var(--gray-muted); font-family: 'JetBrains Mono';">${r.algorithm.replace(/_/g, ' ')}</div>
                </td>
                <td style="font-family: 'JetBrains Mono'; font-weight:600;">${r._calculatedValue.toFixed(2)}</td>
                <td style="font-family: 'JetBrains Mono';">${r.average_runtime_ms.toFixed(4)}</td>
                <td style="font-family: 'JetBrains Mono'; color:var(--cyan);">${r.approximation.toFixed(2)}</td>
                <td>
                    <span style="color: ${r.approximation >= 0.99 ? 'var(--emerald)' : 'var(--amber)'}; font-size:12px; font-weight:500;">
                        ${r.approximation >= 0.99 ? 'Exact' : 'Approximate'}
                    </span>
                </td>
                <td><span class="rank-badge">#${idx + 1}</span></td>
            </tr>`;
        });

        tableHTML += '</tbody></table>';

        // Chart
        let chartHTML = `
            <div class="experiment-chart">
                <div style="font-size: 13px; font-weight: 600; color: var(--cyan); margin-bottom: 16px; text-transform:uppercase; letter-spacing:1px;">
                    Runtime Comparison
                </div>
        `;

        const maxRuntime = Math.max(...results.map(r => r.average_runtime_ms));
        results.forEach(r => {
            const percentage = maxRuntime > 0 ? (r.average_runtime_ms / maxRuntime) * 100 : 100;
            const algoInfo = getAlgoClass(r.algorithm);
            chartHTML += `
                <div class="chart-bar-row">
                    <div class="chart-label">${algoInfo.name}</div>
                    <div class="chart-bar-container">
                        <div class="chart-bar ${algoInfo.css}" style="--bar-width: ${percentage}%">
                            ${r.average_runtime_ms.toFixed(4)}ms
                        </div>
                    </div>
                </div>`;
        });
        chartHTML += '</div>';

        const best = results[0];
        const algoName = getAlgoClass(best.algorithm).name;
        const summary = `
            <div class="experiment-summary">
                <span>Best algorithm for this instance: <b>${algoName}</b> with value <b>${best._calculatedValue.toFixed(2)}</b> achieved in <b>${best.average_runtime_ms.toFixed(4)}ms</b></span>
            </div>`;

        experimentResults.innerHTML = tableHTML + chartHTML + summary;
        
        // Store for PDF export
        currentResults = {
            type: type,
            n: n,
            T: T,
            quality: quality,
            decision: {
                algorithm_name: results[0].algorithm,
                justification: `Based on an experiment comparing ${results.length} algorithms, ${results[0].algorithm} performed best for this instance.`,
                expected_complexity: getComplexityMetrics(results[0].algorithm).time,
                quality_guarantee: results[0].approximation >= 0.99 ? "Exact" : "Approximation"
            },
            solution: results[0].latest_output,
            runtime_ms: results[0].average_runtime_ms,
            experiment: results
        };

        // Add Close Button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'button button-info';
        closeBtn.style.marginTop = '20px';
        closeBtn.innerHTML = '<span>×</span> EXIT EXPERIMENT MODE';
        closeBtn.onclick = () => {
            experimentSection.classList.remove('active');
            const modeBadge = document.getElementById('modeBadge');
            modeBadge.textContent = '[STANDARD MODE]';
            modeBadge.className = 'mode-badge';
            
            // Show experiment button, hide back button
            document.getElementById('experimentBtn').style.display = 'block';
            document.getElementById('backToStandardBtn').style.display = 'none';
        };
        experimentResults.appendChild(closeBtn);

    } catch (e) {
        experimentResults.innerHTML = `<div class="warning-box">Error running experiment: ${e.message}</div>`;
    }
}

// ========== BENCHMARK MODE ==========
let benchmarkCharts = {};

function initBenchmarkCharts() {
    const chartConfigs = [
        { id: 'runtimeChart', type: 'line' },
        { id: 'growthChart', type: 'line' },
        { id: 'complexityChart', type: 'line' },
        { id: 'comparisonChart', type: 'bar' }
    ];

    chartConfigs.forEach(config => {
        const ctx = document.getElementById(config.id).getContext('2d');
        if (benchmarkCharts[config.id]) benchmarkCharts[config.id].destroy();
        
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#9ca3af', font: { family: 'JetBrains Mono' } } }
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } }
            }
        };

        benchmarkCharts[config.id] = new Chart(ctx, {
            type: config.type,
            data: { labels: [], datasets: [] },
            options: commonOptions
        });
    });
}

async function runBenchmark(type) {
    const section = document.getElementById('benchmarkSection');
    const results = document.getElementById('benchmarkResults');
    const stats = document.getElementById('benchmarkStats');

    section.classList.add('active');
    results.innerHTML = '<div class="loading-container"><div class="spinner"></div>Generating scaling data for n=[10, 20, 50, 100, 200]...</div>';
    
    initBenchmarkCharts();

    // Determine algos to benchmark
    let algorithms = [];
    if (type === 'knapsack') algorithms = ['knapsack_dp', 'knapsack_brute_force', 'fractional_knapsack_greedy'];
    else if (type === 'shortest_path') algorithms = ['dijkstra_greedy', 'bellman_ford_dp'];
    else if (type === 'sorting') algorithms = ['merge_sort_dc'];
    else if (type === 'mst') algorithms = ['kruskal_mst_greedy'];
    else if (type === 'matrix_mult') algorithms = ['matrix_multiplication_dc'];
    else if (type === 'searching') algorithms = ['binary_search_dc'];
    else algorithms = ['knapsack_dp', 'fractional_knapsack_greedy'];

    try {
        const response = await callBenchmarkApi(type, algorithms);
        const data = response.benchmark_data;

        if (!data || data.length === 0) {
            results.innerHTML = '<div class="warning-box">Insufficient data for benchmarking.</div>';
            return;
        }

        results.innerHTML = '';
        
        // Group data by algorithm
        const grouped = {};
        data.forEach(item => {
            if (!grouped[item.algorithm]) grouped[item.algorithm] = [];
            grouped[item.algorithm].push(item);
        });

        const inputSizes = [10, 20, 50, 100, 200];
        const colors = ['#00d4ff', '#8b5cf6', '#f59e0b', '#ef4444', '#10b981'];

        // Update Runtime Chart
        benchmarkCharts.runtimeChart.data.labels = inputSizes;
        benchmarkCharts.runtimeChart.data.datasets = Object.keys(grouped).map((algo, i) => ({
            label: getAlgoClass(algo).name,
            data: grouped[algo].map(d => d.runtime_ms),
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length] + '22',
            tension: 0.3,
            fill: true
        }));
        benchmarkCharts.runtimeChart.update();

        // Update Growth Chart (Normalised to n=10)
        benchmarkCharts.growthChart.data.labels = inputSizes;
        benchmarkCharts.growthChart.data.datasets = Object.keys(grouped).map((algo, i) => {
            const base = grouped[algo][0].runtime_ms;
            return {
                label: getAlgoClass(algo).name,
                data: grouped[algo].map(d => base > 0 ? d.runtime_ms / base : 0),
                borderColor: colors[i % colors.length],
                borderDash: [5, 5],
                tension: 0.3
            };
        });
        benchmarkCharts.growthChart.update();

        // Complexity Chart (Theoretical vs Actual)
        // We pick the most complex one to show the "explosion"
        const mainAlgo = Object.keys(grouped).find(a => a.includes('brute_force')) || Object.keys(grouped)[0];
        const theoreticalType = grouped[mainAlgo][0].theoretical_complexity;
        
        const getTheoreticalValue = (n, comp) => {
            if (comp.includes('2^n')) return Math.pow(2, n / 10); // scale for vis
            if (comp.includes('n²')) return n * n / 100;
            if (comp.includes('n log n')) return n * Math.log2(n) / 10;
            if (comp.includes('n')) return n / 10;
            return 0;
        };

        benchmarkCharts.complexityChart.data.labels = inputSizes;
        benchmarkCharts.complexityChart.data.datasets = [
            {
                label: `Actual: ${getAlgoClass(mainAlgo).name}`,
                data: grouped[mainAlgo].map(d => d.runtime_ms),
                borderColor: '#00d4ff',
                pointBackgroundColor: '#00d4ff',
                showLine: true
            },
            {
                label: `Theoretical: ${theoreticalType}`,
                data: inputSizes.map(n => {
                    const actualBase = grouped[mainAlgo][0].runtime_ms;
                    const theoryBase = getTheoreticalValue(inputSizes[0], theoreticalType);
                    const theoryVal = getTheoreticalValue(n, theoreticalType);
                    return theoryBase > 0 ? (theoryVal / theoryBase) * actualBase : theoryVal;
                }),
                borderColor: 'rgba(255,255,255,0.3)',
                borderDash: [2, 2],
                fill: false,
                pointRadius: 0
            }
        ];
        benchmarkCharts.complexityChart.update();

        // Comparison Chart (at max size n=200)
        const maxSizeData = data.filter(d => d.input_size === 200);
        benchmarkCharts.comparisonChart.data.labels = maxSizeData.map(d => getAlgoClass(d.algorithm).name);
        benchmarkCharts.comparisonChart.data.datasets = [{
            label: 'Runtime at n=200 (ms)',
            data: maxSizeData.map(d => d.runtime_ms),
            backgroundColor: colors.slice(0, maxSizeData.length)
        }];
        benchmarkCharts.comparisonChart.update();

        // Update Stats
        const runtimes = data.map(d => d.runtime_ms);
        document.getElementById('algoCount').textContent = Object.keys(grouped).length;
        document.getElementById('fastestResult').textContent = Math.min(...runtimes).toFixed(2) + 'ms';
        
        let pattern = "Polynomial";
        if (theoreticalType.includes('2^n')) pattern = "Exponential ⚠";
        else if (theoreticalType.includes('log')) pattern = "Logarithmic ✓";
        else if (theoreticalType.includes('n log n')) pattern = "Log-Linear";
        document.getElementById('growthPattern').textContent = pattern;

    } catch (e) {
        results.innerHTML = `<div class="warning-box">Benchmark Error: ${e.message}</div>`;
    }
}

// ========== EVENT HANDLERS ==========

document.getElementById('sizeSlider').addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    const range = (value - 2) / (100 - 2);
    e.target.style.setProperty('--range-fill', (range * 100) + '%');
    document.getElementById('nValue').textContent = `n = ${value}`;

    let warning = '';
    if (value > 50) {
        warning = '<div class="warning-badge">⚠ Large input — DP memory intensive</div>';
    } else if (value > 15) {
        const type = document.getElementById('problemType').value;
        if (type === 'subset') {
            warning = '<div class="danger-badge">⚠ Subset enumeration: 2^n = ' + Math.pow(2, value).toLocaleString() + ' states</div>';
        }
    }
    document.getElementById('sizeWarning').innerHTML = warning;
});

document.getElementById('timeSlider').addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    const range = (value - 10) / (10000 - 10);
    e.target.style.setProperty('--range-fill', (range * 100) + '%');
    document.getElementById('tValue').textContent = `T = ${value}ms`;

    let badge = '<span class="time-budget-indicator good">✓ Sufficient Time</span>';
    if (value > 500) {
        badge = '<span class="time-budget-indicator good">✓ ample time</span>';
    } else if (value >= 100 && value <= 500) {
        badge = '<span class="time-budget-indicator warning">⚠ moderate</span>';
    } else if (value < 100) {
        badge = '<span class="time-budget-indicator critical">✗ critical</span>';
    }
    document.getElementById('timeWarning').innerHTML = badge;
});

document.getElementById('solveBtn').addEventListener('click', async () => {
    const type = document.getElementById('problemType').value;
    const n = parseInt(document.getElementById('sizeSlider').value);
    const T = parseInt(document.getElementById('timeSlider').value);
    const quality = document.querySelector('input[name="quality"]:checked').value;

    const modeBadge = document.getElementById('modeBadge');
    modeBadge.textContent = '[STANDARD MODE]';
    modeBadge.className = 'mode-badge';

    renderRecommendation(null);
    document.getElementById('solutionContainer').innerHTML = '<div class="loading-container"><div class="spinner"></div>Loading solution...</div>';

    try {
        const result = await callSolveApi(type, n, T, quality);
        
        // Store for PDF export
        currentResults = {
            type: type,
            n: n,
            T: T,
            quality: quality,
            decision: result.decision,
            solution: result.solution,
            runtime_ms: result.runtime_ms,
            experiment: null
        };

        renderRecommendation(result.decision, type, n, T, quality);
        renderSolutionData(result, type);
        generateFlowchart(result.decision, type, n, T, quality);
    } catch (e) {
        document.getElementById('recommendationContainer').innerHTML = `<div class="warning-box">API Error: ${e.message}</div>`;
        document.getElementById('solutionContainer').innerHTML = '';
    }

    document.getElementById('experimentSection').classList.remove('active');
});

document.getElementById('experimentBtn').addEventListener('click', () => {
    const type = document.getElementById('problemType').value;
    const n = parseInt(document.getElementById('sizeSlider').value);
    const T = parseInt(document.getElementById('timeSlider').value);
    const quality = document.querySelector('input[name="quality"]:checked').value;

    const modeBadge = document.getElementById('modeBadge');
    modeBadge.textContent = '[EXPERIMENT MODE]';
    modeBadge.className = 'mode-badge experiment';

    // Show back button, hide experiment button
    document.getElementById('experimentBtn').style.display = 'none';
    document.getElementById('backToStandardBtn').style.display = 'block';

    runExperiment(type, n, T, quality);
});

document.getElementById('backToStandardBtn').addEventListener('click', () => {
    const experimentSection = document.getElementById('experimentSection');
    experimentSection.classList.remove('active');
    const modeBadge = document.getElementById('modeBadge');
    modeBadge.textContent = '[STANDARD MODE]';
    modeBadge.className = 'mode-badge';
    
    // Show experiment button, hide back button
    document.getElementById('experimentBtn').style.display = 'block';
    document.getElementById('backToStandardBtn').style.display = 'none';
});

document.getElementById('benchmarkBtn').addEventListener('click', () => {
    const type = document.getElementById('problemType').value;
    const modeBadge = document.getElementById('modeBadge');
    modeBadge.textContent = '[BENCHMARK MODE]';
    modeBadge.className = 'mode-badge benchmark';
    
    runBenchmark(type);
});

document.getElementById('closeBenchmarkBtn').addEventListener('click', () => {
    document.getElementById('benchmarkSection').classList.remove('active');
    const modeBadge = document.getElementById('modeBadge');
    modeBadge.textContent = '[STANDARD MODE]';
    modeBadge.className = 'mode-badge';
});

document.getElementById('exportExperimentPdfBtn').addEventListener('click', () => {
    exportPdf();
});

// CSS animation keyframe for dash animation
const style = document.createElement('style');
style.textContent = `
    @keyframes dash {
        to { stroke-dashoffset: -10; }
    }
`;
document.head.appendChild(style);
