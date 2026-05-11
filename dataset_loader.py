import os
import json
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_closest_case(cases, n):
    if not cases:
        return {}
    # Sort by how close their 'n' is to requested 'n'
    cases_sorted = sorted(cases, key=lambda x: abs(x.get('n', 0) - n))
    return cases_sorted[0]

def load_knapsack_case(n: int):
    path = os.path.join(DATA_DIR, "knapsack_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def load_graph_case(n: int):
    path = os.path.join(DATA_DIR, "graph_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def load_sorting_case(n: int):
    path = os.path.join(DATA_DIR, "sorting_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def load_sequence_case(n: int):
    path = os.path.join(DATA_DIR, "sequence_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def get_problem_instance(problem_type: str, n: int):
    # Ensure datasets exist
    import generate_datasets
    if not os.path.exists(os.path.join(DATA_DIR, "knapsack_cases.json")):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(os.path.join(DATA_DIR, "knapsack_cases.json"), "w") as f:
            json.dump(generate_datasets.generate_knapsack_cases(), f)
        with open(os.path.join(DATA_DIR, "graph_cases.json"), "w") as f:
            json.dump(generate_datasets.generate_graph_cases(), f)
        with open(os.path.join(DATA_DIR, "sorting_cases.json"), "w") as f:
            json.dump(generate_datasets.generate_sorting_cases(), f)
        with open(os.path.join(DATA_DIR, "sequence_cases.json"), "w") as f:
            json.dump(generate_datasets.generate_sequence_cases(), f)

    if problem_type in ["knapsack", "fractional_knapsack", "subset"]:
        case = load_knapsack_case(n)
        return {
            "values": case["values"],
            "weights": case["weights"],
            "capacity": case["capacity"]
        }
    elif problem_type in ["mst", "shortest_path"]:
        case = load_graph_case(n)
        return {
            "num_nodes": case["num_nodes"],
            "edges": case["edges"],
            "adjacency": case["adjacency"],
            "source_node": 0
        }
    elif problem_type == "sorting":
        case = load_sorting_case(n)
        return {
            "array": case["array"]
        }
    elif problem_type == "sequence_alignment":
        case = load_sequence_case(n)
        return {
            "seq_a": case["seq_a"],
            "seq_b": case["seq_b"],
            "gap_penalty": case["gap_penalty"],
            "mismatch_penalty": case["mismatch_penalty"]
        }
    elif problem_type == "matrix_mult":
        return {
            # Placeholder for matrix multiplication parameters if any algorithm exists
            "n": n
        }
    return {}
