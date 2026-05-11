// ========== BACKEND INTEGRATION ==========
const API_URL = "http://localhost:5000";

const ALGORITHMS = {
    BRUTE_FORCE: 'knapsack_brute_force', // map to backend identifiers somewhat? Or use the returned
    DYNAMIC_PROGRAMMING: 'knapsack_dp',
    DIVIDE_AND_CONQUER: 'merge_sort_dc',
    GREEDY: 'fractional_knapsack_greedy'
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

        if (solution.dp_table && Array.isArray(solution.dp_table) && solution.dp_table.length <= 50) {
            solutionHTML += '<div style="margin-top: 12px;"><span class="result-row-label">DP Table</span></div>';
            solutionHTML += '<div class="dp-table-container"><table class="dp-table">';
            solution.dp_table.forEach((row, i) => {
                solutionHTML += '<tr>';
                row.slice(0, 20).forEach((col, j) => {
                    solutionHTML += `<td>${col}</td>`;
                });
                if (row.length > 20) solutionHTML += '<td>...</td>';
                solutionHTML += '</tr>';
            });
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
        { x: cx, y: 120, text: 'Check Type', type: 'decision' },                       // 1
        { x: cx, y: 200, text: 'Subset?', type: 'decision' },                          // 2
        { x: leftX, y: 260, text: 'BRUTE FORCE', type: 'algorithm', key: 'brute_force' }, // 3
        { x: cx, y: 280, text: 'DP Suitable?', type: 'decision' },                     // 4
        { x: rightX, y: 340, text: 'DYN. PROG.', type: 'algorithm', key: 'dp' },       // 5
        { x: cx, y: 360, text: 'Sort/Matrix?', type: 'decision' },                     // 6
        { x: leftX, y: 420, text: 'DIV. CONQUER', type: 'algorithm', key: 'dc' },      // 7
        { x: cx, y: 440, text: 'Time/Qual?', type: 'decision' },                       // 8
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
        [0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [4, 6], [6, 7], [6, 8], [8, 9], [3, 10], [5, 10], [7, 10], [9, 10]
    ];

    connections.forEach(([fromIdx, toIdx]) => {
        const from = nodes[fromIdx];
        const to = nodes[toIdx];
        // Ensure path connects visually correctly if active
        const isActive = pathNodes.includes(fromIdx) && pathNodes.includes(toIdx) && 
                         (pathNodes.indexOf(toIdx) === pathNodes.indexOf(fromIdx) + 1);
        drawLine(svg, from, to, isActive);
    });

    nodes.forEach((node, idx) => {
        const isActive = pathNodes.includes(idx);
        drawNode(svg, node, isActive);
    });
}

function drawLine(svg, from, to, active) {
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
            const algoName = getAlgoClass(r.algorithm).name;
            const rowClass = idx === 0 ? 'best' : (idx === results.length - 1 ? 'worst' : '');
            
            tableHTML += `<tr class="${rowClass}">
                <td><strong>${algoName}</strong><br><span style="font-size:10px;color:#888;">${r.algorithm}</span></td>
                <td>${r._calculatedValue.toFixed(2)}</td>
                <td>${r.average_runtime_ms}</td>
                <td>${r.approximation.toFixed(2)}</td>
                <td>${r.approximation >= 0.99 ? 'Exact' : 'Approximate'}</td>
                <td><span class="rank-badge">#${idx + 1}</span></td>
            </tr>`;
        });

        tableHTML += '</tbody></table>';

        // Chart
        let chartHTML = '<div class="experiment-chart"><div style="font-size: 12px; font-weight: 600; color: var(--gray-muted); margin-bottom: 12px;">Runtime Comparison</div>';

        const maxRuntime = Math.max(...results.map(r => r.average_runtime_ms));
        results.forEach(r => {
            const percentage = maxRuntime > 0 ? (r.average_runtime_ms / maxRuntime) * 100 : 100;
            const algoInfo = getAlgoClass(r.algorithm);
            chartHTML += `<div class="chart-bar-row">
                <div class="chart-label">${algoInfo.name}</div>
                <div class="chart-bar-container">
                    <div class="chart-bar ${algoInfo.css}" style="--bar-width: ${percentage}%">${r.average_runtime_ms}ms</div>
                </div>
            </div>`;
        });
        chartHTML += '</div>';

        const best = results[0];
        const algoName = getAlgoClass(best.algorithm).name;
        const summary = `<div class="experiment-summary">
            <strong>Best algorithm for this instance:</strong> ${algoName} with value ${best._calculatedValue.toFixed(2)} achieved in ${best.average_runtime_ms}ms
        </div>`;

        experimentResults.innerHTML = tableHTML + chartHTML + summary;
        
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

// CSS animation keyframe for dash animation
const style = document.createElement('style');
style.textContent = `
    @keyframes dash {
        to { stroke-dashoffset: -10; }
    }
`;
document.head.appendChild(style);
