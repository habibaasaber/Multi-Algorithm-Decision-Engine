
import os
import time
import traceback
import threading
import statistics
import importlib.util
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dataset_loader import get_problem_instance

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
}


#FastAPI Application
app = FastAPI(
    title="Multi-Algorithm Decision Engine API",
    description="Advanced Backend System for Project 19",
    version="1.0.0"
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
    problem_type: str
    n: int = Field(..., gt=0)
    time_budget_ms: float = Field(..., gt=0)
    quality_requirement: str

    parameters: Dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    problem_type: str
    n: int = Field(..., gt=0)
    runs: int = Field(default=3, ge=1, le=20)

    algorithms: List[str]
    parameters: Dict[str, Any] = Field(default_factory=dict)

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

        # STEP 3 → Execute algorithm safely
        solution = run_with_timeout(
            ALGORITHM_FUNCTIONS[algorithm_name],
            timeout_seconds=max(2, request.time_budget_ms / 1000),
            **algo_kwargs
        )

        solution["algorithm_used"] = algorithm_name

        return {
            "status": "success",
            "decision": decision,
            "solution": solution
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
            detail={
                "error": str(error),
                "traceback": traceback.format_exc()
            }
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

# Local Development
if __name__ == "__main__":

    import uvicorn

    print("=" * 60)
    print(" MULTI-ALGORITHM DECISION ENGINE SERVER ")
    print("=" * 60)
    print("Server running on: http://localhost:5000")
    print("Swagger docs:      http://localhost:5000/docs")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000
    )
