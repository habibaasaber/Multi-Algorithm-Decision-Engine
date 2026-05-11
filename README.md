# Multi-Algorithm Decision Engine

## 1. Project Overview
The **Multi-Algorithm Decision Engine** is an intelligent assistant and academic showcase designed to automatically evaluate computational problems and select the optimal algorithm for solving them. By considering parameters such as the problem type, input size, available time budget, and quality requirements (exact vs. approximate), the engine dynamically selects between Dynamic Programming, Divide and Conquer, Greedy, and Brute Force strategies to produce the best result under given constraints.

## 2. Features
- **Intelligent Decision Engine**: Automatically selects the most appropriate algorithm.
- **Multiple Solvers**: Supports Knapsack, Minimum Spanning Tree (MST), Sorting, Shortest Path, Sequence Alignment, Fractional Knapsack, Matrix Multiplication, and Subset Enumeration.
- **FastAPI Backend**: Robust, typed, and scalable backend infrastructure.
- **Dynamic Dataset Loader**: Generates and loads realistic datasets instead of using randomly generated runtimes.
- **Interactive Frontend**: A futuristic, NASA-inspired dashboard with interactive inputs, flowcharts, and solution rendering.
- **Experiment Mode**: Run all applicable algorithms for a given instance, compute their approximation ratios, and rank them by runtime and solution quality.

## 3. Architecture
The project follows a standard client-server architecture:
- **Client (Frontend)**: Written in vanilla HTML, CSS, and JS. It communicates asynchronously via `fetch` to the backend and renders results using dynamic DOM manipulation.
- **Server (Backend)**: Written in Python using FastAPI. It exposes two main endpoints (`/solve` and `/compare`) and integrates with a standalone Python Decision Engine.
- **Data Layer**: JSON datasets representing complex problem structures generated via Python.

## 4. Folder Structure
```
Algorithms/
├── data/
│   ├── knapsack_cases.json
│   ├── graph_cases.json
│   ├── sorting_cases.json
│   └── sequence_cases.json
├── AlgoImpl.py           # Core algorithmic implementations
├── Backend.py            # FastAPI Application and endpoints
├── Decision_Engine.py    # Logic to select the best algorithm
├── dataset_loader.py     # Loader for JSON instances based on input size (n)
├── generate_datasets.py  # Script used to generate the data directory JSON files
├── frontend.js           # Frontend logic and API integration
├── index.html            # User Interface dashboard
└── README.md             # Project documentation
```

## 5. Decision Engine Explanation
The Decision Engine is a rule-based system that operates on a step-by-step fallback mechanism:
1. **Brute Force Check**: Recommended only for extremely small inputs ($n \le 15$) or specific enumeration problems where exhaustive search is required.
2. **Dynamic Programming Check**: Used when exact solutions are required for problems with overlapping subproblems (e.g., Knapsack, Sequence Alignment) and the input size allows fitting the DP table into memory.
3. **Divide and Conquer Check**: Naturally selected for highly structured problems such as Sorting or Matrix Multiplication.
4. **Greedy Check**: Selected if the problem guarantees a greedy optimum (e.g., Fractional Knapsack, MST), if the time budget is critically low, or if the user explicitly permits approximate solutions.
5. **Default**: Falls back to Dynamic Programming.

## 6. Algorithm Descriptions
- **Dynamic Programming (DP)**: Solves Knapsack, Sequence Alignment, and Bellman-Ford using overlapping subproblems. Optimal but memory-intensive ($O(nW)$ or $O(n^2)$).
- **Greedy**: Solves Fractional Knapsack, Kruskal's MST, and Dijkstra. Very fast ($O(n \log n)$) but may not yield the optimal solution for certain problems.
- **Divide and Conquer (DC)**: Solves Sorting (Merge Sort), Binary Search, and Fast Exponentiation by breaking problems into independent subproblems.
- **Brute Force**: Exhaustively evaluates all $2^n$ subsets for problems like 0/1 Knapsack. Guaranteeably exact, but computationally infeasible for large $n$.

## 7. Dataset Explanation
To provide realistic benchmarks and results, problem instances are systematically loaded from JSON files. The dataset system includes:
- `knapsack_cases.json`: Varies in item counts, capacities, weights, and values.
- `graph_cases.json`: Weighted connected graphs appropriate for MST or shortest path testing, ranging from 5 to 50 nodes.
- `sorting_cases.json`: Includes randomized, nearly sorted, and reverse sorted arrays for varied algorithmic stress testing.
- `sequence_cases.json`: DNA-like string pairings simulating sequence alignments with varied mutation rates.

## 8. API Endpoints
- **`GET /health`**: Returns system health, thread status, and loaded algorithms.
- **`POST /solve`**: Takes a `SolveRequest` including `problem_type`, `n`, `time_budget_ms`, and `quality_requirement`. Evaluates the constraints, loads the closest dataset size, and solves the instance using the optimally chosen algorithm.
- **`POST /compare`**: Takes a `CompareRequest`. Evaluates multiple selected algorithms against the same loaded dataset to measure execution time, output exactness, and approximation ratios.

## 9. How to run Backend/Frontend
### Running the Backend
1. Ensure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
3. Run the backend:
   ```bash
   python Backend.py
   ```
   The backend will serve on `http://localhost:5000`.

### Running the Frontend
1. The frontend relies on plain HTML/JS and doesn't require a build step.
2. You can simply open `index.html` in your favorite modern browser.
3. (Optional) Run a lightweight HTTP server for the frontend to prevent any CORS/File protocol issues:
   ```bash
   python -m http.server 8000
   ```
   Then navigate to `http://localhost:8000/index.html`.

## 10. Screenshots
> *(Placeholders for future screenshots)*

![Dashboard View](placeholder_dashboard.png)
*Fig 1: The futuristic main dashboard and recommendation interface.*

![Experiment Mode](placeholder_experiment.png)
*Fig 2: Experiment mode results displaying algorithmic rankings and runtimes.*

## 11. Example Requests / Responses

**Solve Request (`POST /solve`)**
```json
{
  "problem_type": "knapsack",
  "n": 20,
  "time_budget_ms": 1000,
  "quality_requirement": "exact"
}
```

**Solve Response**
```json
{
  "status": "success",
  "decision": {
    "algorithm_name": "knapsack_dp",
    "reason": "Dynamic Programming is optimal for knapsack with exact quality.",
    "time_complexity": "O(nW)",
    "space_complexity": "O(nW)",
    "quality_guarantee": "Exact"
  },
  "solution": {
    "max_value": 450,
    "selected_items": [1, 4, 5, 8],
    "algorithm_used": "knapsack_dp"
  }
}
```
