import os
import time
import traceback
import threading
import statistics
import importlib.util
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Any, List, Optional, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dataset_loader import get_problem_instance
from pdf_generator import generate_report_pdf

# Imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_module(module_name: str, file_name: str):
    """Dynamically load a Python file as a module."""
    file_path = os.path.join(BASE_DIR, file_name)

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load other members files (The path can probably be changed if we changed its path)
algo_module = load_module("algo_module", "AlgoImpl.py")
decision_module = load_module("decision_module", "Decision_Engine.py")

choose_algorithm = decision_module.choose_algorithm

print(f"DEBUG: Loaded AlgoImpl from {os.path.join(BASE_DIR, 'AlgoImpl.py')}")
print(f"DEBUG: Loaded Decision_Engine from {os.path.join(BASE_DIR, 'Decision_Engine.py')}")
print(f"DEBUG: Valid problem types in engine: {getattr(decision_module, 'VALID_PROBLEM_TYPES', 'NOT FOUND')}")



# Algorithm Execution map
ALGORITHM_FUNCTIONS = {
    "knapsack_dp": algo_module.knapsack_dp,
    "sequence_alignment_dp": algo_module.sequence_alignment_dp,
    "bellman_ford_dp": algo_module.bellman_ford_dp,
    "weighted_interval_scheduling_dp": algo_module.weighted_interval_scheduling_dp,
    "fractional_knapsack_greedy": algo_module.fractional_knapsack_greedy,
    "kruskal_mst_greedy": algo_module.kruskal_mst_greedy,
    "dijkstra_greedy": algo_module.dijkstra_greedy,
    "merge_sort_dc": algo_module.merge_sort_dc,
    "binary_search_dc": algo_module.binary_search_dc,
    "fast_exponentiation_dc": algo_module.fast_exponentiation_dc,
    "knapsack_brute_force": algo_module.knapsack_brute_force,
    "subset_bruteforce": algo_module.knapsack_brute_force,  # subset uses knapsack brute force
    "matrix_multiplication_dc": algo_module.matrix_multiplication_dc,
}


#FastAPI Application
app = FastAPI(
    title="Multi-Algorithm Decision Engine API",
    description="Advanced Backend System for Project 19 [VERSION 2.0.1 - FIXED]",
    version="2.0.1"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class SolveRequest(BaseModel):
    problem_type: Literal[
        'exponentiation', 'fractional_knapsack', 'knapsack', 'mst', 
        'scheduling', 'searching', 'sequence_alignment', 'shortest_path', 
        'sorting', 'subset', 'matrix_mult'
    ]
    n: int = Field(..., gt=0)
    time_budget_ms: float = Field(..., gt=0)
    quality_requirement: str

    parameters: Dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    problem_type: Literal[
        'exponentiation', 'fractional_knapsack', 'knapsack', 'mst', 
        'scheduling', 'searching', 'sequence_alignment', 'shortest_path', 
        'sorting', 'subset', 'matrix_mult'
    ]
    n: int = Field(..., gt=0)
    runs: int = Field(default=3, ge=1, le=20)

    algorithms: List[str]
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BenchmarkRequest(BaseModel):
    problem_type: str
    algorithms: List[str]

# Timeout Execution
EXECUTOR = ThreadPoolExecutor(max_workers=4)


def run_with_timeout(func, timeout_seconds=5, **kwargs):
    """Safely execute an algorithm with timeout protection."""

    future = EXECUTOR.submit(func, **kwargs)

    try:
        return future.result(timeout=timeout_seconds)

    except TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Algorithm execution timed out."
        )

    except MemoryError:
        raise HTTPException(
            status_code=507,
            detail="Memory limit exceeded during execution."
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Algorithm execution failed: {str(error)}"
        )

# Helper Functions
def build_algorithm_kwargs(algorithm_name: str, parameters: dict):
    """Extract only required arguments for the selected algorithm."""

    mapping = {
        "knapsack_dp": ["values", "weights", "capacity"],
        "knapsack_brute_force": ["values", "weights", "capacity"],
        "subset_bruteforce": ["values", "weights", "capacity"],
        "fractional_knapsack_greedy": ["values", "weights", "capacity"],

        "sequence_alignment_dp": [
            "seq_a", "seq_b",
            "gap_penalty", "mismatch_penalty"
        ],

        "bellman_ford_dp": [
            "num_nodes", "edges", "source_node"
        ],

        "weighted_interval_scheduling_dp": [
            "intervals"
        ],

        "kruskal_mst_greedy": [
            "num_nodes", "edges"
        ],

        "dijkstra_greedy": [
            "num_nodes", "adjacency", "source_node"
        ],

        "merge_sort_dc": ["array"],

        "binary_search_dc": [
            "sorted_array", "target"
        ],

        "fast_exponentiation_dc": [
            "base", "exponent", "modulus"
        ],
        "matrix_multiplication_dc": [
            "mat_a", "mat_b"
        ],
    }

    required = mapping.get(algorithm_name, [])

    return {
        key: parameters[key]
        for key in required
        if key in parameters
    }


# API Endpoints
@app.get("/")
def root():
    return {
        "project": "Project 19 - Multi-Algorithm Decision Engine",
        "backend": "Member 3 Backend API",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "active_threads": threading.active_count(),
        "algorithms_loaded": len(ALGORITHM_FUNCTIONS)
    }


@app.get("/algorithms")
def list_algorithms():
    return {
        "available_algorithms": sorted(ALGORITHM_FUNCTIONS.keys()),
        "total": len(ALGORITHM_FUNCTIONS)
    }


@app.post("/solve")
def solve_problem(request: SolveRequest):
    """
    Automatically choose and run the best algorithm.
    """

    try:
        # STEP 1 → Auto-load parameters if missing
        if not request.parameters:
            request.parameters = get_problem_instance(request.problem_type, request.n)

        # STEP 2 → Decision Engine
        decision = choose_algorithm(
            problem_type=request.problem_type,
            n=request.n,
            time_budget_ms=request.time_budget_ms,
            quality_requirement=request.quality_requirement,
            **request.parameters
        )

        algorithm_name = decision["algorithm_name"]

        if algorithm_name not in ALGORITHM_FUNCTIONS:
            raise HTTPException(
                status_code=500,
                detail=f"Algorithm '{algorithm_name}' not found."
            )

        # STEP 2 → Prepare parameters
        algo_kwargs = build_algorithm_kwargs(
            algorithm_name,
            request.parameters
        )

        # STEP 3 → Execute algorithm safely (with averaging for stability)
        # We run it once first to get the solution and check performance
        start_time = time.perf_counter()
        solution = run_with_timeout(
            ALGORITHM_FUNCTIONS[algorithm_name],
            timeout_seconds=max(2, request.time_budget_ms / 1000),
            **algo_kwargs
        )
        first_run_ms = (time.perf_counter() - start_time) * 1000

        # If it's fast (< 50ms), run it 99 more times to get a stable average
        if first_run_ms < 50:
            total_time_ms = first_run_ms
            num_runs = 100
            for _ in range(num_runs - 1):
                s = time.perf_counter()
                run_with_timeout(
                    ALGORITHM_FUNCTIONS[algorithm_name],
                    timeout_seconds=1.0,
                    **algo_kwargs
                )
                total_time_ms += (time.perf_counter() - s) * 1000
            avg_runtime_ms = total_time_ms / num_runs
        else:
            avg_runtime_ms = first_run_ms

        solution["algorithm_used"] = algorithm_name

        return {
            "status": "success",
            "decision": decision,
            "solution": solution,
            "runtime_ms": round(avg_runtime_ms, 4)
        }

    except HTTPException:
        raise

    except (ValueError, KeyError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Algorithm execution failed: {str(error)}. Traceback: {traceback.format_exc()}"
        )


@app.post("/export-report")
def export_report(request: SolveRequest):
    """Generate a professional PDF report for the selected experiment."""
    try:
        if not request.parameters:
            request.parameters = get_problem_instance(request.problem_type, request.n)

        decision = choose_algorithm(
            problem_type=request.problem_type,
            n=request.n,
            time_budget_ms=request.time_budget_ms,
            quality_requirement=request.quality_requirement,
            **request.parameters
        )

        algorithm_name = decision["algorithm_name"]
        if algorithm_name not in ALGORITHM_FUNCTIONS:
            raise HTTPException(
                status_code=500,
                detail=f"Algorithm '{algorithm_name}' not found."
            )

        algo_kwargs = build_algorithm_kwargs(
            algorithm_name,
            request.parameters
        )

        start_time = time.perf_counter()
        solution = run_with_timeout(
            ALGORITHM_FUNCTIONS[algorithm_name],
            timeout_seconds=max(2, request.time_budget_ms / 1000),
            **algo_kwargs
        )
        first_run_ms = (time.perf_counter() - start_time) * 1000

        # Stable average runtime if algorithm is very fast
        if first_run_ms < 50:
            total_time_ms = first_run_ms
            num_runs = 100
            for _ in range(num_runs - 1):
                s = time.perf_counter()
                run_with_timeout(
                    ALGORITHM_FUNCTIONS[algorithm_name],
                    timeout_seconds=1.0,
                    **algo_kwargs
                )
                total_time_ms += (time.perf_counter() - s) * 1000
            avg_runtime_ms = total_time_ms / num_runs
        else:
            avg_runtime_ms = first_run_ms

        pdf_bytes = generate_report_pdf(
            decision=decision,
            solution=solution,
            problem_type=request.problem_type,
            runtime_ms=round(avg_runtime_ms, 4),
            n=request.n,
            time_budget_ms=request.time_budget_ms,
            quality_requirement=request.quality_requirement
        )

        return {
            "status": "success",
            "filename": f"report_{request.problem_type}_{int(time.time())}.pdf",
            "pdf_bytes": pdf_bytes.hex(),
            "runtime_ms": round(avg_runtime_ms, 4)
        }

    except HTTPException:
        raise

    except (ValueError, KeyError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(error)}. Traceback: {traceback.format_exc()}"
        )


@app.post("/compare")
def compare_algorithms(request: CompareRequest):
    """
    Run multiple algorithms and compare performance.
    """

    results = []

    try:
        if not request.parameters:
            request.parameters = get_problem_instance(request.problem_type, request.n)

        for algorithm_name in request.algorithms:

            if algorithm_name not in ALGORITHM_FUNCTIONS:
                continue

            runtimes = []
            outputs = []

            algo_kwargs = build_algorithm_kwargs(
                algorithm_name,
                request.parameters
            )

            for _ in range(request.runs):

                start = time.perf_counter()

                result = run_with_timeout(
                    ALGORITHM_FUNCTIONS[algorithm_name],
                    timeout_seconds=10,
                    **algo_kwargs
                )

                end = time.perf_counter()

                runtime_ms = (end - start) * 1000

                runtimes.append(runtime_ms)
                outputs.append(result)

            results.append({
                "algorithm": algorithm_name,
                "runs": request.runs,
                "average_runtime_ms": round(statistics.mean(runtimes), 4),
                "fastest_runtime_ms": round(min(runtimes), 4),
                "slowest_runtime_ms": round(max(runtimes), 4),
                "latest_output": outputs[-1]
            })

        results.sort(
            key=lambda item: item["average_runtime_ms"]
        )

        return {
            "status": "success",
            "problem_type": request.problem_type,
            "comparison_results": results,
            "winner": results[0]["algorithm"] if results else None
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.post("/benchmark")
def run_benchmark(request: BenchmarkRequest):
    """
    Run algorithms across multiple input sizes to analyze scaling and complexity.
    """
    input_sizes = [10, 20, 50, 100, 200]
    results = []

    try:
        for size in input_sizes:
            # Generate/Load proper dataset for this size
            try:
                params = get_problem_instance(request.problem_type, size)
            except Exception as e:
                # Fallback if dataset generation fails
                params = {}

            size_results = []
            for algo_name in request.algorithms:
                if algo_name not in ALGORITHM_FUNCTIONS:
                    continue

                algo_kwargs = build_algorithm_kwargs(algo_name, params)
                
                # Metadata for theoretical complexity
                meta = algo_module.ALGORITHM_REGISTRY.get(algo_name, {})
                theoretical = meta.get("time_complexity", "Unknown")
                
                try:
                    start = time.perf_counter()
                    # We run it 5 times and take the average for smoother curves
                    runtimes = []
                    for _ in range(3):
                        st = time.perf_counter()
                        run_with_timeout(
                            ALGORITHM_FUNCTIONS[algo_name],
                            timeout_seconds=10,
                            **algo_kwargs
                        )
                        runtimes.append((time.perf_counter() - st) * 1000)
                    
                    avg_ms = statistics.mean(runtimes)
                    
                    size_results.append({
                        "algorithm": algo_name,
                        "input_size": size,
                        "runtime_ms": round(avg_ms, 4),
                        "theoretical_complexity": theoretical,
                        "approximation_ratio": meta.get("approx_ratio", 1.0)
                    })
                except Exception as e:
                    # Skip if it fails (e.g. timeout or memory)
                    print(f"Benchmark error for {algo_name} at n={size}: {e}")
                    continue
            
            results.extend(size_results)

        return {
            "status": "success",
            "problem_type": request.problem_type,
            "benchmark_data": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Benchmark failed: {str(error)}"
        )

# Local Development
if __name__ == "__main__":

    import uvicorn

    print("=" * 60)
    print("PROJECT 19 - MULTI-ALGORITHM DECISION ENGINE")
    print("Member 2 - Decision Engine Implementation [VERSION 2.0.1 - FIXED]")
    print("=============================================================")
    print("Server running on: http://localhost:5000")
    print("Swagger docs:      http://localhost:5000/docs")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000
    )
