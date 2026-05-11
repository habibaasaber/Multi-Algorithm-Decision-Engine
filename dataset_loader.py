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

def load_searching_case(n: int):
    path = os.path.join(DATA_DIR, "searching_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def load_exponentiation_case(n: int):
    path = os.path.join(DATA_DIR, "exponentiation_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def load_scheduling_case(n: int):
    path = os.path.join(DATA_DIR, "scheduling_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)

def load_matrix_case(n: int):
    path = os.path.join(DATA_DIR, "matrix_cases.json")
    with open(path, "r") as f:
        cases = json.load(f)
    return get_closest_case(cases, n)


def get_problem_instance(problem_type: str, n: int):
    # Ensure datasets exist
    import generate_datasets
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Check and generate missing dataset files
    datasets = {
        "knapsack_cases.json": generate_datasets.generate_knapsack_cases,
        "graph_cases.json": generate_datasets.generate_graph_cases,
        "sorting_cases.json": generate_datasets.generate_sorting_cases,
        "sequence_cases.json": generate_datasets.generate_sequence_cases,
        "searching_cases.json": generate_datasets.generate_searching_cases,
        "exponentiation_cases.json": generate_datasets.generate_exponentiation_cases,
        "scheduling_cases.json": generate_datasets.generate_scheduling_cases,
        "matrix_cases.json": generate_datasets.generate_matrix_cases,
    }
    
    for filename, generator_func in datasets.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            try:
                with open(filepath, "w") as f:
                    json.dump(generator_func(), f)
            except Exception as e:
                print(f"Warning: Could not generate {filename}: {e}")


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
    elif problem_type == "searching":
        case = load_searching_case(n)
        return {
            "array": case["array"],
            "target": case["target"]
        }
    elif problem_type == "exponentiation":
        case = load_exponentiation_case(n)
        return {
            "base": case["base"],
            "exponent": case["exp"]
        }
    elif problem_type == "scheduling":
        case = load_scheduling_case(n)
        return {
            "intervals": case["intervals"]
        }
    elif problem_type == "matrix_mult":
        case = load_matrix_case(n)
        return {
            "mat_a": case["mat_a"],
            "mat_b": case["mat_b"]
        }

    return {}
