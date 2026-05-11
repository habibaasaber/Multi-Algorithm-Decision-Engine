import json
import random
import os

def generate_knapsack_cases():
    cases = []
    # 50 cases
    for i in range(1, 51):
        # 20 to 100 items
        n_items = random.randint(20, 100)
        capacity = random.randint(50, 500)
        
        values = []
        weights = []
        for _ in range(n_items):
            weights.append(random.randint(1, int(capacity/2) + 1))
            values.append(random.randint(10, 100))
            
        case = {
            "id": i,
            "n": n_items,
            "capacity": capacity,
            "weights": weights,
            "values": values,
            "type": "random"
        }
        cases.append(case)
        
    return cases

def generate_graph_cases():
    cases = []
    # 50 cases
    for i in range(1, 51):
        # 5 to 50 nodes
        num_nodes = random.randint(5, 50)
        edges = []
        # ensure connected (MST/shortest path)
        for j in range(1, num_nodes):
            edges.append({"from": random.randint(0, j-1), "to": j, "weight": random.randint(1, 50)})
        
        # add extra edges
        extra_edges = random.randint(0, num_nodes * 2)
        for _ in range(extra_edges):
            u = random.randint(0, num_nodes-1)
            v = random.randint(0, num_nodes-1)
            if u != v:
                edges.append({"from": u, "to": v, "weight": random.randint(1, 50)})
                
        adjacency = [[] for _ in range(num_nodes)]
        for e in edges:
            adjacency[e["from"]].append({"to": e["to"], "weight": e["weight"]})
            adjacency[e["to"]].append({"to": e["from"], "weight": e["weight"]})

        case = {
            "id": i,
            "n": num_nodes,
            "num_nodes": num_nodes,
            "edges": edges,
            "adjacency": adjacency
        }
        cases.append(case)
        
    return cases

def generate_sorting_cases():
    cases = []
    for i in range(1, 51):
        n = random.randint(20, 500)
        type_ = random.choice(["random", "nearly_sorted", "reverse_sorted"])
        if type_ == "random":
            arr = [random.randint(1, 1000) for _ in range(n)]
        elif type_ == "nearly_sorted":
            arr = list(range(n))
            for _ in range(n // 10):
                idx1, idx2 = random.randint(0, n-1), random.randint(0, n-1)
                arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
        else:
            arr = list(range(n, 0, -1))
            
        case = {
            "id": i,
            "n": n,
            "array": arr,
            "type": type_
        }
        cases.append(case)
    return cases

def generate_sequence_cases():
    cases = []
    dna = ['A', 'T', 'G', 'C']
    for i in range(1, 51):
        n = random.randint(20, 100)
        m = random.randint(20, 100)
        
        seq_a = "".join(random.choice(dna) for _ in range(n))
        
        # seq_b has some mutations
        seq_b_list = list(seq_a)
        if len(seq_b_list) > m:
            seq_b_list = seq_b_list[:m]
        else:
            while len(seq_b_list) < m:
                seq_b_list.append(random.choice(dna))
                
        # mutate
        for _ in range(n // 5):
            idx = random.randint(0, len(seq_b_list)-1)
            seq_b_list[idx] = random.choice(dna)
            
        seq_b = "".join(seq_b_list)
        
        case = {
            "id": i,
            "n": n, # using length of seq_a as n
            "seq_a": seq_a,
            "seq_b": seq_b,
            "gap_penalty": -2,
            "mismatch_penalty": -1
        }
        cases.append(case)
    return cases

def generate_searching_cases():
    cases = []
    for i in range(1, 51):
        n = random.randint(10, 1000)
        arr = sorted([random.randint(1, 5000) for _ in range(n)])
        target = random.choice(arr) if random.random() > 0.2 else random.randint(1, 5000)
        case = {
            "id": i,
            "n": n,
            "array": arr,
            "target": target
        }
        cases.append(case)
    return cases

def generate_exponentiation_cases():
    cases = []
    for i in range(1, 51):
        base = random.randint(2, 10)
        exp = random.randint(10, 100)
        case = {
            "id": i,
            "n": exp, # using exp as n
            "base": base,
            "exp": exp
        }
        cases.append(case)
    return cases

def generate_scheduling_cases():
    cases = []
    for i in range(1, 51):
        n = random.randint(5, 30)
        intervals = []
        for _ in range(n):
            start = random.randint(1, 50)
            end = start + random.randint(1, 20)
            weight = random.randint(10, 100)
            intervals.append((start, end, weight))
        case = {
            "id": i,
            "n": n,
            "intervals": intervals
        }
        cases.append(case)
    return cases

def generate_matrix_cases():
    cases = []
    for i in range(1, 11): # smaller number as matrices are large
        n = 2**random.randint(2, 6) # powers of 2 for Strassen
        mat_a = [[random.randint(1, 10) for _ in range(n)] for _ in range(n)]
        mat_b = [[random.randint(1, 10) for _ in range(n)] for _ in range(n)]
        case = {
            "id": i,
            "n": n,
            "mat_a": mat_a,
            "mat_b": mat_b
        }
        cases.append(case)
    return cases


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    
    with open("data/knapsack_cases.json", "w") as f:
        json.dump(generate_knapsack_cases(), f, indent=2)
        
    with open("data/graph_cases.json", "w") as f:
        json.dump(generate_graph_cases(), f, indent=2)
        
    with open("data/sorting_cases.json", "w") as f:
        json.dump(generate_sorting_cases(), f, indent=2)
        
    with open("data/sequence_cases.json", "w") as f:
        json.dump(generate_sequence_cases(), f, indent=2)

    with open("data/searching_cases.json", "w") as f:
        json.dump(generate_searching_cases(), f, indent=2)

    with open("data/exponentiation_cases.json", "w") as f:
        json.dump(generate_exponentiation_cases(), f, indent=2)

    with open("data/scheduling_cases.json", "w") as f:
        json.dump(generate_scheduling_cases(), f, indent=2)

    with open("data/matrix_cases.json", "w") as f:
        json.dump(generate_matrix_cases(), f, indent=2)

        
    print("Datasets generated successfully.")
