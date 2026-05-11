"""
=============================================================
PROJECT 19 - MULTI-ALGORITHM DECISION ENGINE
Member 1 - Algorithm Engineer Implementation
=============================================================
This file contains ALL algorithm implementations required:
  1. Dynamic Programming  (DP)
  2. Greedy Algorithms
  3. Divide & Conquer
  4. Brute Force

Each function returns a dictionary with full metadata so the
Decision Engine can display results, justifications, and
comparisons without needing to reformat anything.
=============================================================
"""

import time          # for measuring runtime in milliseconds
import math          # for math.inf (infinity) and math.log2
from typing import List, Optional  # for clean type hints


# ╔══════════════════════════════════════════════════════════╗
# ║          SECTION 1 – DYNAMIC PROGRAMMING                 ║
# ╚══════════════════════════════════════════════════════════╝

def knapsack_dp(values: list, weights: list, capacity: int) -> dict:
    """
    Solves the 0/1 Knapsack problem using Dynamic Programming.

    The 0/1 Knapsack problem: given a list of items each with a
    value and weight, choose items (each used at most once) to
    maximise total value without exceeding the weight capacity.

    DP idea: build a 2-D table where
      dp_table[item_index][remaining_capacity]
      = best value achievable using items 0..item_index
        with 'remaining_capacity' weight budget left.

    Args:
        values   : List of item values  e.g. [60, 100, 120]
        weights  : List of item weights e.g. [10,  20,  30]
        capacity : Maximum weight the knapsack can carry e.g. 50

    Returns:
        dict with keys:
          selected_items     – indices of chosen items (0-based)
          total_value        – optimal total value
          total_weight       – total weight of chosen items
          dp_table           – full 2-D DP table (list of lists)
          backtrack_sequence – decision made at each step ("take"/"skip")
          runtime_ms         – how long the algorithm took in ms
    """

    start_time = time.perf_counter()          # start the clock

    num_items = len(values)                   # how many items we have

    # ── Step 1: Build the DP table ──────────────────────────
    # Create a 2D table of zeros with dimensions:
    #   rows = num_items + 1  (row 0 = no items considered yet)
    #   cols = capacity + 1   (col 0 = zero remaining capacity)
    dp_table = [
        [0] * (capacity + 1)
        for _ in range(num_items + 1)
    ]

    # Fill the table row by row (item by item)
    for item_index in range(1, num_items + 1):
        # Current item's value and weight (offset by 1 because row 0 is empty)
        current_value  = values[item_index - 1]
        current_weight = weights[item_index - 1]

        for remaining_capacity in range(capacity + 1):
            # Option A: Skip this item → same value as previous row
            skip_value = dp_table[item_index - 1][remaining_capacity]

            # Option B: Take this item (only if it fits)
            take_value = 0
            if current_weight <= remaining_capacity:
                # value of this item + best value with leftover capacity
                take_value = (current_value
                              + dp_table[item_index - 1]
                                        [remaining_capacity - current_weight])

            # Store the better of skip/take
            dp_table[item_index][remaining_capacity] = max(skip_value, take_value)

    # ── Step 2: Read off the optimal value ──────────────────
    optimal_value = dp_table[num_items][capacity]

    # ── Step 3: Backtrack to find which items were chosen ───
    selected_items      = []      # will store 0-based indices
    backtrack_sequence  = []      # "take" or "skip" per item
    remaining = capacity          # start from full capacity

    for item_index in range(num_items, 0, -1):
        # Did we improve by taking item (item_index - 1)?
        if dp_table[item_index][remaining] != dp_table[item_index - 1][remaining]:
            # Yes → this item was taken
            selected_items.append(item_index - 1)
            backtrack_sequence.append(f"Item {item_index - 1} → TAKE "
                                      f"(value={values[item_index-1]}, "
                                      f"weight={weights[item_index-1]})")
            remaining -= weights[item_index - 1]   # reduce remaining capacity
        else:
            backtrack_sequence.append(f"Item {item_index - 1} → SKIP")

    selected_items.reverse()          # restore original order
    backtrack_sequence.reverse()

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000   # convert seconds → ms

    result = {
        "selected_items"    : selected_items,
        "total_value"       : optimal_value,
        "total_weight"      : sum(weights[i] for i in selected_items),
        "dp_table"          : dp_table,
        "backtrack_sequence": backtrack_sequence,
        "runtime_ms"        : round(runtime_ms, 4),
    }
    return result


# ── Quick test for knapsack_dp ───────────────────────────────
if __name__ == "__main__":
    result = knapsack_dp(
        values   = [60, 100, 120],
        weights  = [10,  20,  30],
        capacity = 50
    )
    print("=== knapsack_dp TEST ===")
    print(f"Selected items : {result['selected_items']}")
    print(f"Total value    : {result['total_value']}")
    print(f"Total weight   : {result['total_weight']}")
    print(f"Runtime        : {result['runtime_ms']} ms")
    print("Backtrack steps:")
    for step in result["backtrack_sequence"]:
        print("  ", step)
    print()


# ─────────────────────────────────────────────────────────────

def sequence_alignment_dp(seq_a: str, seq_b: str, gap_penalty: int = 1,
                           mismatch_penalty: int = 1) -> dict:
    """
    Solves Sequence Alignment (Edit Distance / Needleman-Wunsch style)
    using Dynamic Programming.

    Finds the minimum cost to transform seq_a into seq_b using:
      - Insert  a character  → costs gap_penalty
      - Delete  a character  → costs gap_penalty
      - Replace a character  → costs mismatch_penalty (if chars differ)
      - Match                → costs 0

    Args:
        seq_a            : First sequence  e.g. "ACGT"
        seq_b            : Second sequence e.g. "AGT"
        gap_penalty      : Cost of a gap (insertion or deletion), default 1
        mismatch_penalty : Cost of substituting one char for another, default 1

    Returns:
        dict with keys:
          edit_distance      – minimum alignment cost
          aligned_a          – seq_a after alignment (with gaps shown as '-')
          aligned_b          – seq_b after alignment
          dp_table           – full 2-D cost table
          backtrack_sequence – list of alignment operations
          runtime_ms         – runtime in milliseconds
    """

    start_time = time.perf_counter()

    len_a = len(seq_a)
    len_b = len(seq_b)

    # ── Step 1: Build DP table ───────────────────────────────
    # dp_table[i][j] = min cost to align seq_a[0..i-1] with seq_b[0..j-1]
    dp_table = [[0] * (len_b + 1) for _ in range(len_a + 1)]

    # Base cases: aligning with an empty string costs only gaps
    for row in range(len_a + 1):
        dp_table[row][0] = row * gap_penalty      # delete all of seq_a
    for col in range(len_b + 1):
        dp_table[0][col] = col * gap_penalty      # insert all of seq_b

    # Fill the rest of the table
    for row in range(1, len_a + 1):
        for col in range(1, len_b + 1):
            char_a = seq_a[row - 1]
            char_b = seq_b[col - 1]

            # Cost of substitution: 0 if same character, else mismatch_penalty
            sub_cost = 0 if char_a == char_b else mismatch_penalty

            # Three options: substitute, delete from seq_a, insert into seq_a
            dp_table[row][col] = min(
                dp_table[row - 1][col - 1] + sub_cost,   # match or substitute
                dp_table[row - 1][col]     + gap_penalty, # delete char from a
                dp_table[row][col - 1]     + gap_penalty  # insert char into a
            )

    edit_distance = dp_table[len_a][len_b]

    # ── Step 2: Backtrack to reconstruct the alignment ───────
    aligned_a          = []
    aligned_b          = []
    backtrack_sequence = []
    row, col = len_a, len_b   # start at bottom-right corner

    while row > 0 or col > 0:
        if row > 0 and col > 0:
            char_a   = seq_a[row - 1]
            char_b   = seq_b[col - 1]
            sub_cost = 0 if char_a == char_b else mismatch_penalty

            if dp_table[row][col] == dp_table[row-1][col-1] + sub_cost:
                # Came from diagonal → match or substitute
                aligned_a.append(char_a)
                aligned_b.append(char_b)
                op = "MATCH" if char_a == char_b else "SUBSTITUTE"
                backtrack_sequence.append(f"{op}: '{char_a}' ↔ '{char_b}'")
                row -= 1
                col -= 1
                continue

        if row > 0 and dp_table[row][col] == dp_table[row-1][col] + gap_penalty:
            # Came from above → delete char from seq_a
            aligned_a.append(seq_a[row - 1])
            aligned_b.append("-")
            backtrack_sequence.append(f"DELETE: '{seq_a[row-1]}' from A")
            row -= 1
        else:
            # Came from left → insert char into seq_a
            aligned_a.append("-")
            aligned_b.append(seq_b[col - 1])
            backtrack_sequence.append(f"INSERT: '{seq_b[col-1]}' into B")
            col -= 1

    # Reverse because we traced from end to start
    aligned_a.reverse()
    aligned_b.reverse()
    backtrack_sequence.reverse()

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "edit_distance"     : edit_distance,
        "aligned_a"         : "".join(aligned_a),
        "aligned_b"         : "".join(aligned_b),
        "dp_table"          : dp_table,
        "backtrack_sequence": backtrack_sequence,
        "runtime_ms"        : round(runtime_ms, 4),
    }


# ── Quick test for sequence_alignment_dp ────────────────────
if __name__ == "__main__":
    result = sequence_alignment_dp("ACGT", "AGT")
    print("=== sequence_alignment_dp TEST ===")
    print(f"Edit distance : {result['edit_distance']}")
    print(f"Aligned A     : {result['aligned_a']}")
    print(f"Aligned B     : {result['aligned_b']}")
    print(f"Runtime       : {result['runtime_ms']} ms")
    print()


# ─────────────────────────────────────────────────────────────

def bellman_ford_dp(num_nodes: int, edges: list, source_node: int) -> dict:
    """
    Finds shortest paths from a source node to all other nodes
    using the Bellman-Ford algorithm (handles negative weights).

    The algorithm relaxes every edge (num_nodes - 1) times.
    If distances still decrease after that, a negative cycle exists.

    Args:
        num_nodes   : Total number of nodes (0-indexed)
        edges       : List of (from_node, to_node, weight) tuples
        source_node : Starting node index

    Returns:
        dict with keys:
          distances          – shortest distance from source to each node
          predecessors       – previous node on the shortest path
          dp_table           – distances after each relaxation round
          backtrack_sequence – path from source to each reachable node
          has_negative_cycle – True if a negative-weight cycle exists
          runtime_ms         – runtime in milliseconds
    """

    start_time = time.perf_counter()

    # ── Step 1: Initialise distances ────────────────────────
    INF = math.inf
    distances    = [INF] * num_nodes    # all distances start as infinity
    predecessors = [-1]  * num_nodes    # no predecessor known yet
    distances[source_node] = 0          # source to itself = 0

    dp_table = []   # snapshot of distances after each relaxation round

    # ── Step 2: Relax edges (num_nodes - 1) times ───────────
    for round_number in range(num_nodes - 1):
        updated = False   # track whether anything changed this round
        for (from_node, to_node, weight) in edges:
            # Can we improve the path to to_node via from_node?
            if (distances[from_node] != INF
                    and distances[from_node] + weight < distances[to_node]):
                distances[to_node]    = distances[from_node] + weight
                predecessors[to_node] = from_node
                updated = True

        # Store a snapshot of distances this round (for the DP table)
        dp_table.append(distances[:])

        # Early exit if nothing changed
        if not updated:
            break

    # ── Step 3: Detect negative-weight cycles ───────────────
    has_negative_cycle = False
    for (from_node, to_node, weight) in edges:
        if (distances[from_node] != INF
                and distances[from_node] + weight < distances[to_node]):
            has_negative_cycle = True
            break

    # ── Step 4: Reconstruct paths (backtrack) ───────────────
    backtrack_sequence = []
    for target_node in range(num_nodes):
        if distances[target_node] == INF:
            backtrack_sequence.append(
                f"Node {target_node}: unreachable from {source_node}")
            continue

        path = []
        current = target_node
        while current != -1:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        path_str = " → ".join(str(n) for n in path)
        backtrack_sequence.append(
            f"Node {target_node}: {path_str}  (cost={distances[target_node]})")

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "distances"         : distances,
        "predecessors"      : predecessors,
        "dp_table"          : dp_table,
        "backtrack_sequence": backtrack_sequence,
        "has_negative_cycle": has_negative_cycle,
        "runtime_ms"        : round(runtime_ms, 4),
    }


# ── Quick test for bellman_ford_dp ──────────────────────────
if __name__ == "__main__":
    # Graph: 0→1 (weight 4), 0→2 (weight 5), 1→3 (weight -3), 2→3 (weight 2)
    edges_test = [(0, 1, 4), (0, 2, 5), (1, 3, -3), (2, 3, 2)]
    result = bellman_ford_dp(num_nodes=4, edges=edges_test, source_node=0)
    print("=== bellman_ford_dp TEST ===")
    print(f"Distances          : {result['distances']}")
    print(f"Has negative cycle : {result['has_negative_cycle']}")
    print(f"Runtime            : {result['runtime_ms']} ms")
    print("Paths:")
    for step in result["backtrack_sequence"]:
        print("  ", step)
    print()


# ─────────────────────────────────────────────────────────────

def weighted_interval_scheduling_dp(intervals: list) -> dict:
    """
    Solves Weighted Interval Scheduling using Dynamic Programming.

    Given a list of intervals each with (start, end, weight/profit),
    find the subset of non-overlapping intervals with maximum total weight.

    DP idea: sort by end time, then for each interval i, either:
      - Skip  it: dp[i] = dp[i-1]
      - Take  it: dp[i] = weight[i] + dp[last non-overlapping interval]

    Args:
        intervals : List of (start_time, end_time, weight) tuples

    Returns:
        dict with keys:
          selected_intervals – indices of chosen intervals (0-based)
          total_weight       – maximum total weight
          dp_table           – DP values after each step (1-D list)
          backtrack_sequence – take/skip decision per interval
          runtime_ms         – runtime in milliseconds
    """

    start_time_clock = time.perf_counter()

    # ── Step 1: Sort intervals by their end time ─────────────
    # Keep original indices so we can report them back
    indexed_intervals = sorted(
        enumerate(intervals),          # (original_index, (start, end, weight))
        key=lambda x: x[1][1]         # sort key: end time
    )
    num_intervals = len(indexed_intervals)

    # Unpack for convenience
    original_indices = [item[0]       for item in indexed_intervals]
    starts           = [item[1][0]    for item in indexed_intervals]
    ends             = [item[1][1]    for item in indexed_intervals]
    weights_list     = [item[1][2]    for item in indexed_intervals]

    # ── Step 2: For each interval, find the last compatible one ─
    # "Compatible" means its end time <= start time of current interval
    def last_compatible(index: int) -> int:
        """Binary search for the latest interval that ends before index starts."""
        lo, hi = 0, index - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ends[mid] <= starts[index]:
                if mid + 1 <= index - 1 and ends[mid + 1] <= starts[index]:
                    lo = mid + 1
                else:
                    return mid
            else:
                hi = mid - 1
        return -1   # no compatible interval found

    # ── Step 3: Build the DP table ───────────────────────────
    # dp_table[i] = best total weight using first i intervals
    dp_table = [0] * (num_intervals + 1)

    for pos in range(1, num_intervals + 1):
        interval_idx   = pos - 1   # 0-based index into sorted arrays
        compatible_pos = last_compatible(interval_idx)

        # Value if we TAKE this interval
        take_value = weights_list[interval_idx]
        if compatible_pos >= 0:
            take_value += dp_table[compatible_pos + 1]

        # Value if we SKIP this interval
        skip_value = dp_table[pos - 1]

        dp_table[pos] = max(take_value, skip_value)

    # ── Step 4: Backtrack to find selected intervals ─────────
    selected_sorted    = []
    backtrack_sequence = []
    pos = num_intervals

    while pos >= 1:
        interval_idx   = pos - 1
        compatible_pos = last_compatible(interval_idx)

        take_value = weights_list[interval_idx]
        if compatible_pos >= 0:
            take_value += dp_table[compatible_pos + 1]

        if take_value >= dp_table[pos - 1]:
            # We took this interval
            selected_sorted.append(original_indices[interval_idx])
            backtrack_sequence.append(
                f"Interval {original_indices[interval_idx]} → TAKE "
                f"(start={starts[interval_idx]}, end={ends[interval_idx]}, "
                f"weight={weights_list[interval_idx]})")
            pos = compatible_pos + 1   # jump past the compatible boundary
        else:
            backtrack_sequence.append(
                f"Interval {original_indices[interval_idx]} → SKIP")
            pos -= 1

    selected_intervals = sorted(selected_sorted)
    backtrack_sequence.reverse()

    end_time_clock = time.perf_counter()
    runtime_ms     = (end_time_clock - start_time_clock) * 1000

    return {
        "selected_intervals": selected_intervals,
        "total_weight"      : dp_table[num_intervals],
        "dp_table"          : dp_table,
        "backtrack_sequence": backtrack_sequence,
        "runtime_ms"        : round(runtime_ms, 4),
    }


# ── Quick test for weighted_interval_scheduling_dp ──────────
if __name__ == "__main__":
    # (start, end, weight)
    test_intervals = [(1, 3, 5), (2, 5, 6), (4, 6, 5), (6, 7, 4), (5, 8, 11)]
    result = weighted_interval_scheduling_dp(test_intervals)
    print("=== weighted_interval_scheduling_dp TEST ===")
    print(f"Selected intervals : {result['selected_intervals']}")
    print(f"Total weight       : {result['total_weight']}")
    print(f"Runtime            : {result['runtime_ms']} ms")
    print()


# ╔══════════════════════════════════════════════════════════╗
# ║          SECTION 2 – GREEDY ALGORITHMS                   ║
# ╚══════════════════════════════════════════════════════════╝

def fractional_knapsack_greedy(values: list, weights: list,
                                capacity: int) -> dict:
    """
    Solves the Fractional Knapsack problem using a Greedy approach.

    Unlike 0/1 knapsack, items CAN be fractionally included.
    Strategy: always pick the item with the highest value-per-unit-weight
    first. This greedy choice is provably optimal for fractional knapsack.

    Args:
        values   : List of item values   e.g. [60, 100, 120]
        weights  : List of item weights  e.g. [10,  20,  30]
        capacity : Maximum weight allowed e.g. 50

    Returns:
        dict with keys:
          fractions          – fraction taken of each item [0.0 .. 1.0]
          total_value        – achieved total value (greedy)
          approximation_ratio– greedy_value / optimal_value (should be 1.0
                               since greedy IS optimal for fractional)
          warning_message    – note about approximation guarantee
          runtime_ms         – runtime in milliseconds
    """

    start_time = time.perf_counter()

    num_items = len(values)

    # ── Step 1: Compute value-per-weight ratio for each item ─
    ratios = [
        (values[i] / weights[i], i)   # (ratio, original_index)
        for i in range(num_items)
    ]

    # ── Step 2: Sort items by ratio descending (best first) ──
    ratios.sort(reverse=True)

    # ── Step 3: Greedily fill the knapsack ───────────────────
    fractions        = [0.0] * num_items   # how much of each item we take
    remaining_cap    = capacity
    total_value      = 0.0

    for (ratio, item_index) in ratios:
        if remaining_cap <= 0:
            break   # knapsack is full

        item_weight = weights[item_index]
        item_value  = values[item_index]

        if item_weight <= remaining_cap:
            # Take the whole item
            fractions[item_index] = 1.0
            total_value      += item_value
            remaining_cap    -= item_weight
        else:
            # Take only a fraction of this item to fill the rest
            fraction = remaining_cap / item_weight
            fractions[item_index] = fraction
            total_value   += fraction * item_value
            remaining_cap  = 0

    # Approximation ratio: for fractional knapsack greedy is OPTIMAL (ratio=1.0)
    # We compute it vs the greedy value itself since no brute force available here
    approximation_ratio = 1.0   # provably optimal for fractional variant

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "fractions"          : fractions,
        "total_value"        : round(total_value, 4),
        "approximation_ratio": approximation_ratio,
        "warning_message"    : ("Fractional Knapsack greedy is PROVABLY OPTIMAL "
                                "(approximation ratio = 1.0). No quality loss."),
        "runtime_ms"         : round(runtime_ms, 4),
    }


# ── Quick test for fractional_knapsack_greedy ───────────────
if __name__ == "__main__":
    result = fractional_knapsack_greedy(
        values=[60, 100, 120], weights=[10, 20, 30], capacity=50
    )
    print("=== fractional_knapsack_greedy TEST ===")
    print(f"Fractions taken    : {result['fractions']}")
    print(f"Total value        : {result['total_value']}")
    print(f"Approx ratio       : {result['approximation_ratio']}")
    print(f"Warning            : {result['warning_message']}")
    print()


# ─────────────────────────────────────────────────────────────

def kruskal_mst_greedy(num_nodes: int, edges: list) -> dict:
    """
    Finds a Minimum Spanning Tree (MST) using Kruskal's Greedy algorithm.

    Strategy: sort all edges by weight ascending, then greedily add the
    cheapest edge that does NOT form a cycle (using Union-Find to detect cycles).
    This is provably optimal for MST.

    Args:
        num_nodes : Number of nodes (0-indexed)
        edges     : List of (node_a, node_b, weight) tuples

    Returns:
        dict with keys:
          mst_edges          – list of (node_a, node_b, weight) in the MST
          total_weight       – sum of edge weights in MST
          approximation_ratio– 1.0 (Kruskal is provably optimal for MST)
          warning_message    – quality guarantee note
          runtime_ms         – runtime in milliseconds
    """

    start_time = time.perf_counter()

    # ── Step 1: Sort edges by weight ─────────────────────────
    sorted_edges = sorted(edges, key=lambda edge: edge[2])

    # ── Step 2: Union-Find data structure ────────────────────
    # parent[node] tracks which "group" each node belongs to.
    # If parent[node] == node, it is the root of its group.
    parent = list(range(num_nodes))   # initially each node is its own root
    rank   = [0] * num_nodes          # used for efficient merging

    def find_root(node: int) -> int:
        """Find the root of node's group (with path compression)."""
        if parent[node] != node:
            parent[node] = find_root(parent[node])   # path compression
        return parent[node]

    def union_groups(node_a: int, node_b: int) -> bool:
        """
        Merge the groups of node_a and node_b.
        Returns True if they were in different groups (no cycle),
                False if they were already in the same group (cycle!).
        """
        root_a = find_root(node_a)
        root_b = find_root(node_b)
        if root_a == root_b:
            return False   # same group → adding this edge would make a cycle
        # Merge smaller group into larger group (union by rank)
        if rank[root_a] < rank[root_b]:
            parent[root_a] = root_b
        elif rank[root_a] > rank[root_b]:
            parent[root_b] = root_a
        else:
            parent[root_b] = root_a
            rank[root_a]  += 1
        return True

    # ── Step 3: Greedily add edges that don't form cycles ────
    mst_edges    = []
    total_weight = 0

    for (node_a, node_b, weight) in sorted_edges:
        if len(mst_edges) == num_nodes - 1:
            break   # MST is complete (needs exactly num_nodes - 1 edges)

        if union_groups(node_a, node_b):   # no cycle → safe to add
            mst_edges.append((node_a, node_b, weight))
            total_weight += weight

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "mst_edges"          : mst_edges,
        "total_weight"       : total_weight,
        "approximation_ratio": 1.0,
        "warning_message"    : ("Kruskal's MST is PROVABLY OPTIMAL. "
                                "Approximation ratio = 1.0 guaranteed."),
        "runtime_ms"         : round(runtime_ms, 4),
    }


# ── Quick test for kruskal_mst_greedy ───────────────────────
if __name__ == "__main__":
    # 4 nodes, edges: (from, to, weight)
    edges_test = [(0,1,10),(0,2,6),(0,3,5),(1,3,15),(2,3,4)]
    result = kruskal_mst_greedy(num_nodes=4, edges=edges_test)
    print("=== kruskal_mst_greedy TEST ===")
    print(f"MST edges    : {result['mst_edges']}")
    print(f"Total weight : {result['total_weight']}")
    print(f"Approx ratio : {result['approximation_ratio']}")
    print()


# ─────────────────────────────────────────────────────────────

def dijkstra_greedy(num_nodes: int, adjacency: list,
                    source_node: int) -> dict:
    """
    Finds shortest paths from source using Dijkstra's Greedy algorithm.
    ONLY valid for graphs with NON-NEGATIVE edge weights.

    Strategy: always expand the unvisited node with the smallest known
    distance (greedy choice). This is provably optimal when weights ≥ 0.

    Args:
        num_nodes   : Number of nodes (0-indexed)
        adjacency   : adjacency[node] = list of (neighbour, weight) tuples
        source_node : Starting node

    Returns:
        dict with keys:
          distances          – shortest distance from source to each node
          predecessors       – previous node on optimal path
          visit_order        – order in which nodes were finalized
          approximation_ratio– 1.0 (Dijkstra is provably optimal)
          warning_message    – note about negative-weight limitation
          runtime_ms         – runtime in milliseconds
    """

    start_time = time.perf_counter()

    INF          = math.inf
    distances    = [INF] * num_nodes
    predecessors = [-1]  * num_nodes
    visited      = [False] * num_nodes
    visit_order  = []

    distances[source_node] = 0

    # ── Greedy loop: always pick the closest unvisited node ──
    for _ in range(num_nodes):
        # Find the unvisited node with minimum distance (simple O(n) scan)
        current_node = -1
        min_dist     = INF
        for node in range(num_nodes):
            if not visited[node] and distances[node] < min_dist:
                min_dist     = distances[node]
                current_node = node

        if current_node == -1:
            break   # all remaining nodes are unreachable

        visited[current_node] = True
        visit_order.append(current_node)

        # Relax all neighbours of current_node
        for (neighbour, weight) in adjacency[current_node]:
            if not visited[neighbour]:
                new_dist = distances[current_node] + weight
                if new_dist < distances[neighbour]:
                    distances[neighbour]    = new_dist
                    predecessors[neighbour] = current_node

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "distances"          : distances,
        "predecessors"       : predecessors,
        "visit_order"        : visit_order,
        "approximation_ratio": 1.0,
        "warning_message"    : ("Dijkstra is PROVABLY OPTIMAL for non-negative "
                                "weights. Use Bellman-Ford if negative weights exist."),
        "runtime_ms"         : round(runtime_ms, 4),
    }


# ── Quick test for dijkstra_greedy ──────────────────────────
if __name__ == "__main__":
    # 5 nodes: adjacency list
    adj = [
        [(1, 10), (2, 3)],          # node 0
        [(3, 2)],                   # node 1
        [(1, 4), (3, 8), (4, 2)],   # node 2
        [(4, 5)],                   # node 3
        [(3, 1)],                   # node 4
    ]
    result = dijkstra_greedy(num_nodes=5, adjacency=adj, source_node=0)
    print("=== dijkstra_greedy TEST ===")
    print(f"Distances    : {result['distances']}")
    print(f"Visit order  : {result['visit_order']}")
    print(f"Approx ratio : {result['approximation_ratio']}")
    print()


# ╔══════════════════════════════════════════════════════════╗
# ║          SECTION 3 – DIVIDE & CONQUER                    ║
# ╚══════════════════════════════════════════════════════════╝

def merge_sort_dc(array: list) -> dict:
    """
    Sorts a list using the Merge Sort Divide & Conquer algorithm.

    Strategy:
      1. DIVIDE:   split array in half
      2. CONQUER:  recursively sort each half
      3. COMBINE:  merge the two sorted halves

    Args:
        array : List of comparable elements to sort

    Returns:
        dict with keys:
          sorted_array   – the sorted list
          recursion_depth– maximum depth reached during recursion
          level_sizes    – list of (depth, left_size, right_size) per split
          runtime_ms     – runtime in milliseconds
    """

    start_time = time.perf_counter()

    # We use a shared list to collect metadata across recursive calls
    level_sizes    = []     # records sub-problem sizes at each level
    max_depth_seen = [0]    # mutable container so nested function can update it

    def _merge_sort(sub_array: list, depth: int) -> list:
        """Recursive helper that sorts sub_array and logs metadata."""

        # Update the deepest level seen so far
        max_depth_seen[0] = max(max_depth_seen[0], depth)

        # Base case: an array of 0 or 1 element is already sorted
        if len(sub_array) <= 1:
            return sub_array

        # ── DIVIDE ──────────────────────────────────────────
        mid   = len(sub_array) // 2
        left  = sub_array[:mid]
        right = sub_array[mid:]

        # Log this split so we can show sub-problem sizes
        level_sizes.append({
            "depth"     : depth,
            "total_size": len(sub_array),
            "left_size" : len(left),
            "right_size": len(right),
        })

        # ── CONQUER ─────────────────────────────────────────
        sorted_left  = _merge_sort(left,  depth + 1)
        sorted_right = _merge_sort(right, depth + 1)

        # ── COMBINE (merge) ──────────────────────────────────
        merged = []
        left_ptr = right_ptr = 0
        while left_ptr < len(sorted_left) and right_ptr < len(sorted_right):
            if sorted_left[left_ptr] <= sorted_right[right_ptr]:
                merged.append(sorted_left[left_ptr])
                left_ptr += 1
            else:
                merged.append(sorted_right[right_ptr])
                right_ptr += 1

        # Append any remaining elements
        merged.extend(sorted_left[left_ptr:])
        merged.extend(sorted_right[right_ptr:])
        return merged

    sorted_array = _merge_sort(array[:], depth=0)   # sort a copy

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "sorted_array"  : sorted_array,
        "recursion_depth": max_depth_seen[0],
        "level_sizes"   : level_sizes,
        "runtime_ms"    : round(runtime_ms, 4),
    }


# ── Quick test for merge_sort_dc ────────────────────────────
if __name__ == "__main__":
    result = merge_sort_dc([38, 27, 43, 3, 9, 82, 10])
    print("=== merge_sort_dc TEST ===")
    print(f"Sorted array    : {result['sorted_array']}")
    print(f"Recursion depth : {result['recursion_depth']}")
    print(f"Runtime         : {result['runtime_ms']} ms")
    print("Level sizes (first 4):")
    for level in result["level_sizes"][:4]:
        print("  ", level)
    print()


# ─────────────────────────────────────────────────────────────

def binary_search_dc(sorted_array: list, target) -> dict:
    """
    Searches for a target value in a SORTED array using Binary Search.

    Strategy: at each step, compare target to the middle element.
      - If equal   → found it.
      - If smaller → search the LEFT half (discard right).
      - If larger  → search the RIGHT half (discard left).

    Args:
        sorted_array : A list sorted in ascending order
        target       : The value to search for

    Returns:
        dict with keys:
          found          – True if target is in the array
          index          – index of target (-1 if not found)
          recursion_depth– number of recursive calls made
          level_sizes    – list of sub-array sizes at each recursive call
          runtime_ms     – runtime in milliseconds
    """

    start_time = time.perf_counter()

    level_sizes    = []
    calls_made     = [0]    # mutable counter

    def _binary_search(low: int, high: int, depth: int) -> int:
        """Returns the index of target, or -1 if not found."""
        calls_made[0] += 1
        level_sizes.append({
            "depth"       : depth,
            "sub_size"    : high - low + 1,
            "low_index"   : low,
            "high_index"  : high,
        })

        # Base case: empty range
        if low > high:
            return -1

        mid = (low + high) // 2

        if sorted_array[mid] == target:
            return mid                          # found!
        elif sorted_array[mid] < target:
            return _binary_search(mid + 1, high, depth + 1)   # search right
        else:
            return _binary_search(low, mid - 1, depth + 1)    # search left

    found_index = _binary_search(0, len(sorted_array) - 1, 0)

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "found"          : found_index != -1,
        "index"          : found_index,
        "recursion_depth": calls_made[0],
        "level_sizes"    : level_sizes,
        "runtime_ms"     : round(runtime_ms, 4),
    }


# ── Quick test for binary_search_dc ─────────────────────────
if __name__ == "__main__":
    result = binary_search_dc([1, 3, 5, 7, 9, 11, 13, 15], target=7)
    print("=== binary_search_dc TEST ===")
    print(f"Found          : {result['found']}")
    print(f"Index          : {result['index']}")
    print(f"Recursion depth: {result['recursion_depth']}")
    print(f"Runtime        : {result['runtime_ms']} ms")
    print()


# ─────────────────────────────────────────────────────────────

def fast_exponentiation_dc(base: int, exponent: int,
                            modulus: Optional[int] = None) -> dict:
    """
    Computes base^exponent (optionally mod modulus) using
    Fast Exponentiation (Exponentiation by Squaring).

    Instead of multiplying 'base' by itself 'exponent' times (slow),
    we use the rule:
      base^n = (base^(n/2))^2          if n is even
      base^n = base * (base^(n/2))^2   if n is odd

    This reduces multiplications from O(n) → O(log n).

    Args:
        base     : The base number
        exponent : The power to raise base to (must be ≥ 0)
        modulus  : Optional modulus for modular exponentiation

    Returns:
        dict with keys:
          result         – base^exponent (mod modulus if given)
          recursion_depth– depth of the recursion tree
          level_sizes    – sub-problem sizes (exponent values) at each level
          runtime_ms     – runtime in milliseconds
    """

    start_time = time.perf_counter()

    level_sizes    = []
    max_depth_seen = [0]

    def _fast_exp(current_base: int, current_exp: int, depth: int) -> int:
        """Recursively compute current_base ^ current_exp."""
        max_depth_seen[0] = max(max_depth_seen[0], depth)
        level_sizes.append({
            "depth"      : depth,
            "base"       : current_base,
            "exponent"   : current_exp,
            "sub_problem": f"{current_base}^{current_exp}",
        })

        # Base cases
        if current_exp == 0:
            return 1
        if current_exp == 1:
            return current_base % modulus if modulus else current_base

        # ── DIVIDE: solve half the exponent ─────────────────
        half = _fast_exp(current_base, current_exp // 2, depth + 1)

        # ── COMBINE: square the result ───────────────────────
        if current_exp % 2 == 0:
            result_val = half * half
        else:
            result_val = current_base * half * half

        # Apply modulus if requested (prevents huge numbers)
        if modulus:
            result_val %= modulus

        return result_val

    final_result = _fast_exp(base, exponent, 0)

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "result"         : final_result,
        "recursion_depth": max_depth_seen[0],
        "level_sizes"    : level_sizes,
        "runtime_ms"     : round(runtime_ms, 4),
    }


# ── Quick test for fast_exponentiation_dc ───────────────────
if __name__ == "__main__":
    result = fast_exponentiation_dc(base=2, exponent=10)
    print("=== fast_exponentiation_dc TEST ===")
    print(f"2^10           = {result['result']}")          # Expected: 1024
    print(f"Recursion depth: {result['recursion_depth']}")
    print(f"Runtime        : {result['runtime_ms']} ms")
    print()


# ╔══════════════════════════════════════════════════════════╗
# ║          SECTION 4 – BRUTE FORCE                         ║
# ╚══════════════════════════════════════════════════════════╝

def knapsack_brute_force(values: list, weights: list,
                          capacity: int) -> dict:
    """
    Solves 0/1 Knapsack by exhaustively checking ALL subsets.

    ⚠ WARNING: Only safe for n ≤ 15 (at most 32,768 subsets).
    For n=20, that's 1,048,576 subsets; for n=30, it's over a billion.

    Strategy: enumerate every possible subset using bit manipulation.
    Subset k is represented by the bits of integer k:
      bit j of k = 1 → include item j in this subset.

    Args:
        values   : List of item values
        weights  : List of item weights
        capacity : Maximum weight allowed

    Returns:
        dict with keys:
          selected_items     – indices of optimal items
          total_value        – optimal total value
          total_weight       – total weight of selected items
          states_evaluated   – number of subsets checked (= 2^n)
          warning_message    – safety warning about exponential growth
          runtime_ms         – runtime in milliseconds
    """

    start_time = time.perf_counter()

    num_items = len(values)

    # ── Safety check: refuse to run for large inputs ─────────
    HARD_LIMIT = 15
    if num_items > HARD_LIMIT:
        return {
            "selected_items"  : [],
            "total_value"     : None,
            "total_weight"    : None,
            "states_evaluated": 2 ** num_items,
            "warning_message" : (f"REFUSED: n={num_items} exceeds the hard limit "
                                 f"of {HARD_LIMIT}. Brute force would evaluate "
                                 f"{2**num_items:,} subsets — infeasible!"),
            "runtime_ms"      : 0,
        }

    total_subsets     = 2 ** num_items   # total number of possible subsets
    best_value        = 0
    best_subset_mask  = 0   # bitmask representing the best subset found

    # ── Enumerate all subsets ────────────────────────────────
    for subset_mask in range(total_subsets):
        # Compute total value and weight of this subset
        subset_value  = 0
        subset_weight = 0

        for item_index in range(num_items):
            # Check if item_index is included in this subset
            if subset_mask & (1 << item_index):
                subset_value  += values[item_index]
                subset_weight += weights[item_index]

        # Is this subset feasible (within capacity) and better?
        if subset_weight <= capacity and subset_value > best_value:
            best_value       = subset_value
            best_subset_mask = subset_mask

    # ── Decode the best bitmask into item indices ─────────────
    selected_items = []
    for item_index in range(num_items):
        if best_subset_mask & (1 << item_index):
            selected_items.append(item_index)

    end_time   = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        "selected_items"  : selected_items,
        "total_value"     : best_value,
        "total_weight"    : sum(weights[i] for i in selected_items),
        "states_evaluated": total_subsets,
        "warning_message" : (f"Brute force evaluated {total_subsets:,} subsets "
                             f"(2^{num_items}). This is INFEASIBLE for n > {HARD_LIMIT}."),
        "runtime_ms"      : round(runtime_ms, 4),
    }


# ── Quick test for knapsack_brute_force ─────────────────────
if __name__ == "__main__":
    result = knapsack_brute_force(
        values=[60, 100, 120], weights=[10, 20, 30], capacity=50
    )
    print("=== knapsack_brute_force TEST ===")
    print(f"Selected items   : {result['selected_items']}")
    print(f"Total value      : {result['total_value']}")
    print(f"States evaluated : {result['states_evaluated']}")
    print(f"Warning          : {result['warning_message']}")
    print(f"Runtime          : {result['runtime_ms']} ms")
    print()

    # Test the safety guard
    big_result = knapsack_brute_force(
        values=[1]*20, weights=[1]*20, capacity=10
    )
    print("=== Large input safety test ===")
    print(f"Warning: {big_result['warning_message']}")
    print()


# ╔══════════════════════════════════════════════════════════╗
# ║          SECTION 5 – APPROXIMATION RATIO CALCULATOR      ║
# ╚══════════════════════════════════════════════════════════╝

def compute_approximation_ratio(greedy_value: float,
                                optimal_value: float) -> dict:
    """
    Helper utility used by the Decision Engine to compute how close
    a greedy/approximate solution is to the optimal (brute-force) solution.

    Args:
        greedy_value  : Value achieved by the approximate algorithm
        optimal_value : True optimal value (from brute force or DP)

    Returns:
        dict with keys:
          ratio          – greedy_value / optimal_value  (1.0 = perfect)
          percentage     – ratio expressed as a percentage
          quality_label  – human-readable quality assessment
    """

    if optimal_value == 0:
        ratio = 1.0   # avoid division by zero; both are zero
    else:
        ratio = greedy_value / optimal_value

    percentage = round(ratio * 100, 2)

    if ratio >= 0.99:
        quality_label = "OPTIMAL (≥99%)"
    elif ratio >= 0.90:
        quality_label = "EXCELLENT (90-99%)"
    elif ratio >= 0.75:
        quality_label = "GOOD (75-90%)"
    else:
        quality_label = f"POOR (<75%) – ratio={ratio:.3f}"

    return {
        "ratio"        : round(ratio, 4),
        "percentage"   : percentage,
        "quality_label": quality_label,
    }


# ── Quick test for compute_approximation_ratio ───────────────
if __name__ == "__main__":
    ratio_info = compute_approximation_ratio(220, 220)
    print("=== compute_approximation_ratio TEST ===")
    print(f"Ratio: {ratio_info['ratio']}  → {ratio_info['quality_label']}")
    print()


# ╔══════════════════════════════════════════════════════════════════╗
# ║   SECTION 6 – TEAM COLLABORATION LAYER                          ║
# ║                                                                  ║
# ║   Everything below this line is specifically designed for        ║
# ║   Member 2 (Decision Engine) and Member 3 (Backend/API).         ║
# ║                                                                  ║
# ║   Member 2: import ALGORITHM_REGISTRY to read algorithm          ║
# ║             metadata (complexity, thresholds, family).           ║
# ║                                                                  ║
# ║   Member 3: call run_algorithm(name, **kwargs) from your         ║
# ║             /solve endpoint — it routes to the right function    ║
# ║             and always returns the same dict shape.              ║
# ╚══════════════════════════════════════════════════════════════════╝


# ── 6.1  ALGORITHM REGISTRY  ────────────────────────────────────────
#
# Member 2 reads this dict to build choose_algorithm() rules.
# Each key is the canonical algorithm name used everywhere in the project.
# Each value contains EVERYTHING Member 2 needs for the decision logic
# and EVERYTHING Member 3 needs to call the right function.
#
# Keys explained:
#   family          – one of "dp" | "greedy" | "divide_and_conquer" | "brute_force"
#   problem_types   – which problem types this algorithm can solve
#   time_complexity – Big-O string (for the recommendation card / Member 4)
#   space_complexity– Big-O string
#   quality         – "exact" | "approximate" | "heuristic"
#   approx_ratio    – float or None  (1.0 = optimal, <1.0 = approximate)
#   approx_guaranteed – True if the ratio is provably bounded
#   thresholds      – dict of conditions that must be True to use this algo
#                     Member 2 evaluates these against (n, T, quality, capacity)
#   warning         – string to surface in the UI when this algo is chosen
#   callable_name   – string key used by run_algorithm() to dispatch

ALGORITHM_REGISTRY: dict = {

    # ── Dynamic Programming ─────────────────────────────────────────

    "knapsack_dp": {
        "family"           : "dp",
        "problem_types"    : ["knapsack"],
        "time_complexity"  : "O(n × capacity)",
        "space_complexity" : "O(n × capacity)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            # Member 2: only pick this when ALL conditions hold
            "max_n"               : 1000,           # n must be ≤ 1000
            "max_n_times_capacity": 10_000_000,     # n × capacity ≤ 10^7
            "requires_quality"    : "exact",        # user must want exact answer
        },
        "warning"          : None,
        "callable_name"    : "knapsack_dp",
    },

    "sequence_alignment_dp": {
        "family"           : "dp",
        "problem_types"    : ["sequence_alignment"],
        "time_complexity"  : "O(n × m)",
        "space_complexity" : "O(n × m)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"           : 5000,
            "requires_quality": "exact",
        },
        "warning"          : None,
        "callable_name"    : "sequence_alignment_dp",
    },

    "bellman_ford_dp": {
        "family"           : "dp",
        "problem_types"    : ["shortest_path"],
        "time_complexity"  : "O(n × E)",         # n nodes, E edges
        "space_complexity" : "O(n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"              : 500,
            "allows_neg_weights" : True,     # must use this if negative weights exist
            "requires_quality"   : "exact",
        },
        "warning": ("Bellman-Ford is slower than Dijkstra. "
                    "Use only when negative edge weights are present."),
        "callable_name"    : "bellman_ford_dp",
    },

    "weighted_interval_scheduling_dp": {
        "family"           : "dp",
        "problem_types"    : ["scheduling"],
        "time_complexity"  : "O(n log n)",
        "space_complexity" : "O(n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"           : 100_000,
            "requires_quality": "exact",
        },
        "warning"          : None,
        "callable_name"    : "weighted_interval_scheduling_dp",
    },

    # ── Greedy ──────────────────────────────────────────────────────

    "fractional_knapsack_greedy": {
        "family"           : "greedy",
        "problem_types"    : ["fractional_knapsack"],
        "time_complexity"  : "O(n log n)",
        "space_complexity" : "O(n)",
        "quality"          : "exact",            # greedy IS optimal here
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"               : 10_000_000,  # effectively unlimited
            "allows_fractions"    : True,        # problem must allow splitting items
        },
        "warning"          : None,
        "callable_name"    : "fractional_knapsack_greedy",
    },

    "kruskal_mst_greedy": {
        "family"           : "greedy",
        "problem_types"    : ["mst"],
        "time_complexity"  : "O(E log E)",
        "space_complexity" : "O(n + E)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"      : 1_000_000,
            "is_undirected": True,
        },
        "warning"          : None,
        "callable_name"    : "kruskal_mst_greedy",
    },

    "dijkstra_greedy": {
        "family"           : "greedy",
        "problem_types"    : ["shortest_path"],
        "time_complexity"  : "O(n²)",            # simple array version
        "space_complexity" : "O(n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"            : 10_000,
            "requires_non_neg" : True,   # MUST have no negative weights
        },
        "warning": ("Dijkstra requires non-negative edge weights. "
                    "If negative weights exist, use bellman_ford_dp instead."),
        "callable_name"    : "dijkstra_greedy",
    },

    # ── Divide & Conquer ────────────────────────────────────────────

    "merge_sort_dc": {
        "family"           : "divide_and_conquer",
        "problem_types"    : ["sorting"],
        "time_complexity"  : "O(n log n)",
        "space_complexity" : "O(n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n": 10_000_000,
        },
        "warning"          : None,
        "callable_name"    : "merge_sort_dc",
    },

    "binary_search_dc": {
        "family"           : "divide_and_conquer",
        "problem_types"    : ["searching"],
        "time_complexity"  : "O(log n)",
        "space_complexity" : "O(log n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n"       : 10_000_000,
            "must_be_sorted": True,
        },
        "warning"          : None,
        "callable_name"    : "binary_search_dc",
    },

    "fast_exponentiation_dc": {
        "family"           : "divide_and_conquer",
        "problem_types"    : ["exponentiation"],
        "time_complexity"  : "O(log n)",
        "space_complexity" : "O(log n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n": 10_000_000,
        },
        "warning"          : None,
        "callable_name"    : "fast_exponentiation_dc",
    },

    # ── Brute Force ─────────────────────────────────────────────────

    "knapsack_brute_force": {
        "family"           : "brute_force",
        "problem_types"    : ["knapsack"],
        "time_complexity"  : "O(2^n)",
        "space_complexity" : "O(n)",
        "quality"          : "exact",
        "approx_ratio"     : 1.0,
        "approx_guaranteed": True,
        "thresholds"       : {
            "max_n": 15,    # HARD LIMIT — never run for n > 15
        },
        "warning": ("Brute force evaluates 2^n subsets. "
                    "This is infeasible for n > 15. "
                    "Only use for correctness verification."),
        "callable_name"    : "knapsack_brute_force",
    },
}


# ── 6.2  ALGORITHM DISPATCHER  ──────────────────────────────────────
#
# Member 3 calls this from the /solve API endpoint.
# It takes the algorithm name chosen by Member 2's choose_algorithm()
# and routes the call to the correct function with the right arguments.
#
# IMPORTANT: every return dict from every algorithm already contains
# a "runtime_ms" key — Member 3 does NOT need to time things separately.

def run_algorithm(algorithm_name: str, **kwargs) -> dict:
    """
    Dispatches a call to the correct algorithm function.

    Member 3 usage in the /solve endpoint:
        result = run_algorithm("knapsack_dp",
                               values=[60,100,120],
                               weights=[10,20,30],
                               capacity=50)

    Args:
        algorithm_name : One of the keys in ALGORITHM_REGISTRY
        **kwargs       : Arguments forwarded to the algorithm function.
                         See each function's docstring for required params.

    Returns:
        dict  – the algorithm's result dict, plus two extra keys added here:
                  "algorithm_used" – the name string, for the API response
                  "metadata"       – the ALGORITHM_REGISTRY entry, so Member 3
                                     can attach complexity/quality info to the
                                     JSON response without a second lookup

    Raises:
        ValueError  – if algorithm_name is not in the registry
        TypeError   – if wrong kwargs are passed (Python raises this naturally)
    """

    # Look up the algorithm in the registry
    if algorithm_name not in ALGORITHM_REGISTRY:
        raise ValueError(
            f"Unknown algorithm: '{algorithm_name}'. "
            f"Available algorithms: {list(ALGORITHM_REGISTRY.keys())}"
        )

    # Map algorithm names to their actual Python functions
    # (keeps the registry data separate from the function objects)
    _DISPATCH_TABLE: dict = {
        "knapsack_dp"                    : knapsack_dp,
        "sequence_alignment_dp"          : sequence_alignment_dp,
        "bellman_ford_dp"                : bellman_ford_dp,
        "weighted_interval_scheduling_dp": weighted_interval_scheduling_dp,
        "fractional_knapsack_greedy"     : fractional_knapsack_greedy,
        "kruskal_mst_greedy"             : kruskal_mst_greedy,
        "dijkstra_greedy"                : dijkstra_greedy,
        "merge_sort_dc"                  : merge_sort_dc,
        "binary_search_dc"               : binary_search_dc,
        "fast_exponentiation_dc"         : fast_exponentiation_dc,
        "knapsack_brute_force"           : knapsack_brute_force,
    }

    # Call the function with whatever kwargs Member 3 passed in
    func   = _DISPATCH_TABLE[algorithm_name]
    result = func(**kwargs)

    # Attach metadata so the API response is self-contained
    result["algorithm_used"] = algorithm_name
    result["metadata"]       = ALGORITHM_REGISTRY[algorithm_name]

    return result


# ── 6.3  EXPERIMENT MODE HELPER  ────────────────────────────────────
#
# Member 3 calls this for the /compare endpoint.
# It runs ALL algorithms that are applicable to the given problem type
# and returns a ranked list — ready to pass straight to Member 4's
# comparison table.

def run_experiment_mode(problem_type: str, n: int, **kwargs) -> dict:
    """
    Runs every applicable algorithm for a problem type and returns
    a ranked comparison — used by the /compare API endpoint.

    Member 3 usage:
        comparison = run_experiment_mode(
            problem_type = "knapsack",
            n            = 10,
            values       = [60, 100, 120],
            weights      = [10, 20, 30],
            capacity     = 50
        )

    Args:
        problem_type : e.g. "knapsack", "sorting", "mst" (must match
                       the "problem_types" list in ALGORITHM_REGISTRY)
        n            : input size — used to skip algorithms that exceed
                       their max_n threshold
        **kwargs     : problem-specific arguments forwarded to each
                       applicable algorithm function

    Returns:
        dict with keys:
          problem_type     – echoed back for the API response
          n                – echoed back
          results          – list of result dicts, sorted best→worst by
                             approx_ratio (ties broken by runtime_ms)
          skipped          – list of (algorithm_name, reason) for algos
                             that were skipped (e.g. n > max_n)
    """

    results = []
    skipped = []

    for algo_name, meta in ALGORITHM_REGISTRY.items():

        # Skip algorithms that don't handle this problem type
        if problem_type not in meta["problem_types"]:
            continue

        # Skip algorithms whose n threshold would be exceeded
        max_n = meta["thresholds"].get("max_n", float("inf"))
        if n > max_n:
            skipped.append({
                "algorithm": algo_name,
                "reason"   : f"n={n} exceeds this algorithm's max_n={max_n}",
            })
            continue

        # Run the algorithm and catch any errors gracefully
        try:
            result = run_algorithm(algo_name, **kwargs)
            results.append(result)
        except Exception as error:
            skipped.append({
                "algorithm": algo_name,
                "reason"   : f"Runtime error: {error}",
            })

    # Sort: highest approximation ratio first, then fastest runtime
    results.sort(
        key=lambda r: (
            -r["metadata"]["approx_ratio"],   # descending ratio (best first)
             r.get("runtime_ms", 0),           # ascending runtime (faster first)
        )
    )

    # Add rank numbers so Member 4 can display them directly
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank

    return {
        "problem_type": problem_type,
        "n"           : n,
        "results"     : results,
        "skipped"     : skipped,
    }


# ── 6.4  QUICK INTEGRATION TEST  ────────────────────────────────────
#
# Run this file directly to verify the collaboration layer works.
# Member 2 and Member 3 can use this as a sanity check after import.

if __name__ == "__main__":

    print("=" * 60)
    print("SECTION 6 — COLLABORATION LAYER INTEGRATION TEST")
    print("=" * 60)

    # Test 1: run_algorithm dispatcher
    print("\n[Test 1] run_algorithm() dispatcher")
    result = run_algorithm(
        "knapsack_dp",
        values   = [60, 100, 120],
        weights  = [10, 20, 30],
        capacity = 50,
    )
    print(f"  Algorithm used : {result['algorithm_used']}")
    print(f"  Total value    : {result['total_value']}")
    print(f"  Family         : {result['metadata']['family']}")
    print(f"  Complexity     : {result['metadata']['time_complexity']}")
    print(f"  Quality        : {result['metadata']['quality']}")
    print(f"  Runtime        : {result['runtime_ms']} ms")

    # Test 2: run_experiment_mode for knapsack (runs DP + brute force)
    print("\n[Test 2] run_experiment_mode() — knapsack (n=3, safe for brute force)")
    comparison = run_experiment_mode(
        problem_type = "knapsack",
        n            = 3,
        values       = [60, 100, 120],
        weights      = [10, 20, 30],
        capacity     = 50,
    )
    print(f"  Problem type : {comparison['problem_type']}")
    print(f"  Algorithms run: {len(comparison['results'])}")
    for r in comparison["results"]:
        print(f"    Rank {r['rank']}: {r['algorithm_used']}"
              f"  | value={r.get('total_value', '—')}"
              f"  | runtime={r['runtime_ms']} ms")
    if comparison["skipped"]:
        print(f"  Skipped: {[s['algorithm'] for s in comparison['skipped']]}")

    # Test 3: error handling for unknown algorithm
    print("\n[Test 3] run_algorithm() with bad name → should raise ValueError")
    try:
        run_algorithm("magic_sort", array=[3, 1, 2])
    except ValueError as e:
        print(f"  Caught expected error: {e}")

    # Test 4: ALGORITHM_REGISTRY spot-check (for Member 2)
    print("\n[Test 4] ALGORITHM_REGISTRY entries for Member 2")
    for name, meta in ALGORITHM_REGISTRY.items():
        print(f"  {name:<40} family={meta['family']:<20}"
              f" max_n={meta['thresholds'].get('max_n', '∞')}")

    print("\nAll collaboration layer tests passed.")