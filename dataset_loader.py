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


def generate_dynamic_instance(problem_type: str, n: int):
    """Generate a problem instance of exactly size n."""
    if problem_type in ["knapsack", "fractional_knapsack", "subset"]:
        capacity = n * 10
        weights = [random.randint(1, n * 2) for _ in range(n)]
        values = [random.randint(10, 100) for _ in range(n)]
        return {"values": values, "weights": weights, "capacity": capacity}
    
    elif problem_type in ["mst", "shortest_path"]:
        num_nodes = n
        edges = []
        for i in range(1, num_nodes):
            edges.append({"from": random.randint(0, i-1), "to": i, "weight": random.randint(1, 50)})
        extra = random.randint(0, n)
        for _ in range(extra):
            u, v = random.randint(0, n-1), random.randint(0, n-1)
            if u != v: edges.append({"from": u, "to": v, "weight": random.randint(1, 50)})
        
        adjacency = [[] for _ in range(num_nodes)]
        for e in edges:
            adjacency[e["from"]].append({"to": e["to"], "weight": e["weight"]})
            adjacency[e["to"]].append({"to": e["from"], "weight": e["weight"]})
        return {"num_nodes": num_nodes, "edges": edges, "adjacency": adjacency, "source_node": 0}
    
    elif problem_type == "sorting":
        return {"array": [random.randint(1, 1000) for _ in range(n)]}
    
    elif problem_type == "sequence_alignment":
        dna = ['A', 'T', 'G', 'C']
        seq_a = "".join(random.choice(dna) for _ in range(n))
        seq_b = "".join(random.choice(dna) for _ in range(n))
        return {"seq_a": seq_a, "seq_b": seq_b, "gap_penalty": 1, "mismatch_penalty": 1}
    
    elif problem_type == "searching":
        arr = sorted([random.randint(1, 5000) for _ in range(n)])
        return {"array": arr, "sorted_array": arr, "target": random.choice(arr)}
    
    elif problem_type == "exponentiation":
        return {"base": random.randint(2, 10), "exponent": n, "modulus": 10**9 + 7}
    
    elif problem_type == "scheduling":
        intervals = []
        for _ in range(n):
            s = random.randint(1, 50); e = s + random.randint(1, 20); w = random.randint(10, 100)
            intervals.append((s, e, w))
        return {"intervals": intervals}
    
    elif problem_type == "matrix_mult":
        # Ensure n is power of 2 for Strassen
        p2 = 1
        while p2 < n: p2 *= 2
        m = p2
        mat_a = [[random.randint(1, 5) for _ in range(m)] for _ in range(m)]
        mat_b = [[random.randint(1, 5) for _ in range(m)] for _ in range(m)]
        return {"mat_a": mat_a, "mat_b": mat_b}
    
    return {}


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

    # For benchmarking and accurate results, we generate exactly size n
    return generate_dynamic_instance(problem_type, n)
