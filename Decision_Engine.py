"""
=============================================================
PROJECT 19 - MULTI-ALGORITHM DECISION ENGINE
Member 2 - Decision Engine Implementation [VERSION 2.0.1 - FIXED]
=============================================================
This file contains the Decision Engine logic:
    choose_algorithm(problem_type, n, time_budget_ms,
                     quality_requirement, **kwargs)

It uses ALGORITHM_REGISTRY from Member 1 to pick the best
algorithm based on the problem type, input size, time budget,
and quality requirement.

How to use (Member 3 calls this):
    from member2_decision_engine import choose_algorithm
    decision = choose_algorithm(
        problem_type       = "knapsack",
        n                  = 20,
        time_budget_ms     = 500,
        quality_requirement= "exact",
        capacity           = 100,
        has_negative_weights = False
    )
=============================================================
"""

# ── Import the registry from Member 1's file ────────────────
# Member 3: make sure AlgoImpl.py is in the same folder
from AlgoImpl import ALGORITHM_REGISTRY


# ╔══════════════════════════════════════════════════════════╗
# ║         VALID PROBLEM TYPES (from the registry)          ║
# ╚══════════════════════════════════════════════════════════╝

# All problem types that the engine knows about
VALID_PROBLEM_TYPES = {
    "knapsack",
    "fractional_knapsack",
    "sequence_alignment",
    "shortest_path",
    "scheduling",
    "mst",
    "sorting",
    "searching",
    "exponentiation",
    "subset",
    "matrix_mult",
}


# ╔══════════════════════════════════════════════════════════╗
# ║              MAIN DECISION ENGINE FUNCTION               ║
# ╚══════════════════════════════════════════════════════════╝

def choose_algorithm(
    problem_type: str,
    n: int,
    time_budget_ms: float,
    quality_requirement: str,
    **kwargs
) -> dict:
    """
    Selects the most appropriate algorithm for the given problem.

    Decision Rules (applied in order):
      1. Validate all inputs → raise ValueError for bad inputs
      2. Handle Divide & Conquer problems first (sorting/searching/exponentiation)
         - Binary search requires sorted array check
      3. Handle MST problems → Kruskal (always greedy-optimal)
      4. Handle Scheduling → Weighted Interval Scheduling DP
      5. Handle Sequence Alignment → DP
      6. Handle Shortest Path:
         - Negative weights → Bellman-Ford (DP)
         - No negative weights + n small → Dijkstra (Greedy)
      7. Handle Knapsack:
         - fractional_knapsack → Fractional Knapsack Greedy
         - quality == "approximate" OR time_budget_ms < 100 → Greedy (fractional)
         - n <= 15 AND quality == "exact" → Brute Force
         - quality == "exact" AND n*capacity within threshold → DP
         - Fallback → Greedy
      8. Fallback error if nothing matched

    Args:
        problem_type        : One of VALID_PROBLEM_TYPES
        n                   : Input size (must be > 0)
        time_budget_ms      : Available time in ms (must be > 0)
        quality_requirement : "exact" | "approximate" | "best_effort"
        **kwargs:
          capacity              (int)  – for knapsack
          has_negative_weights  (bool) – for shortest_path
          is_sorted             (bool) – for searching
          is_undirected         (bool) – for mst

    Returns:
        dict with keys:
          algorithm_name     – canonical name from ALGORITHM_REGISTRY
          justification      – one-paragraph explanation for the UI
          expected_complexity– Big-O string from the registry
          quality_guarantee  – human-readable quality label
          warnings           – list of warning strings (may be empty)
    """

    warnings = []

    # ══════════════════════════════════════════════════════
    # STEP 1 — INPUT VALIDATION
    # ══════════════════════════════════════════════════════

    # n must be a positive integer
    if not isinstance(n, int) or n <= 0:
        raise ValueError(
            f"Invalid input size n={n!r}. "
            "n must be a positive integer greater than 0."
        )

    # time_budget_ms must be positive
    if not isinstance(time_budget_ms, (int, float)) or time_budget_ms <= 0:
        raise ValueError(
            f"Invalid time_budget_ms={time_budget_ms!r}. "
            "Must be a positive number (milliseconds)."
        )

    # problem_type must be known
    if problem_type not in VALID_PROBLEM_TYPES:
        raise ValueError(
            f"Unknown problem_type={problem_type!r}. "
            f"Valid types: {sorted(VALID_PROBLEM_TYPES)}"
        )

    # quality_requirement must be one of the accepted values
    if quality_requirement not in ("exact", "approximate", "best_effort"):
        raise ValueError(
            f"Invalid quality_requirement={quality_requirement!r}. "
            "Must be 'exact', 'approximate', or 'best_effort'."
        )

    # ══════════════════════════════════════════════════════
    # STEP 2 — DIVIDE & CONQUER PROBLEMS
    # (sorting, searching, exponentiation)
    # ══════════════════════════════════════════════════════

    if problem_type == "sorting":
        # Merge sort is always the right choice for sorting
        meta = ALGORITHM_REGISTRY["merge_sort_dc"]
        return _build_result(
            algorithm_name = "merge_sort_dc",
            justification  = (
                "Divide & Conquer (Merge Sort) selected. "
                "The problem type is sorting, which has optimal "
                "sub-structure and independent sub-problems — "
                "a perfect fit for D&C. Merge Sort guarantees "
                f"O(n log n) time with exact results for any n "
                f"up to {meta['thresholds']['max_n']:,}. "
                f"Input size n={n} is within this limit."
            ),
            meta     = meta,
            warnings = warnings,
        )

    if problem_type == "searching":
        # Binary search requires a sorted array
        is_sorted = kwargs.get("is_sorted", None)
        if is_sorted is False:
            raise ValueError(
                "Binary search requires a sorted array. "
                "Set is_sorted=True only when the array is already sorted, "
                "or sort it first using the sorting problem type."
            )
        if is_sorted is None:
            warnings.append(
                "is_sorted was not specified. "
                "Binary search ONLY works on sorted arrays. "
                "Verify the array is sorted before proceeding."
            )
        meta = ALGORITHM_REGISTRY["binary_search_dc"]
        return _build_result(
            algorithm_name = "binary_search_dc",
            justification  = (
                "Divide & Conquer (Binary Search) selected. "
                "Searching problems with a sorted array are solved "
                "optimally by Binary Search in O(log n) time. "
                "Each step halves the search space, making this "
                "extremely efficient even for very large n."
            ),
            meta     = meta,
            warnings = warnings,
        )

    if problem_type == "exponentiation":
        meta = ALGORITHM_REGISTRY["fast_exponentiation_dc"]
        return _build_result(
            algorithm_name = "fast_exponentiation_dc",
            justification  = (
                "Divide & Conquer (Fast Exponentiation) selected. "
                "Exponentiation by squaring reduces the number of "
                "multiplications from O(n) to O(log n) by splitting "
                "the exponent in half at each recursive step. "
                "This is the provably optimal approach for this problem."
            ),
            meta     = meta,
            warnings = warnings,
        )

    if problem_type == "matrix_mult":
        meta = ALGORITHM_REGISTRY["matrix_multiplication_dc"]
        if n > meta["thresholds"]["max_n"]:
            raise ValueError(
                f"n={n} exceeds the maximum supported size "
                f"({meta['thresholds']['max_n']}) for Strassen's matrix mult. "
                "The recursion depth would be too great."
            )
        return _build_result(
            algorithm_name = "matrix_multiplication_dc",
            justification  = (
                "Divide & Conquer (Strassen's Algorithm) selected. "
                "Matrix multiplication can be improved from O(n³) to "
                "O(n^log₂7) by recursively splitting matrices into "
                "quadrants and performing 7 multiplications instead of 8. "
                f"For n={n}, this approach is highly efficient."
            ),
            meta     = meta,
            warnings = warnings,
        )

    # ══════════════════════════════════════════════════════
    # STEP 3 — MST PROBLEM
    # ══════════════════════════════════════════════════════

    if problem_type == "mst":
        meta = ALGORITHM_REGISTRY["kruskal_mst_greedy"]
        return _build_result(
            algorithm_name = "kruskal_mst_greedy",
            justification  = (
                "Greedy (Kruskal's MST) selected. "
                "Minimum Spanning Tree problems are solved provably "
                "optimally by Kruskal's greedy algorithm. It sorts "
                "edges by weight and adds the cheapest edge that "
                "doesn't form a cycle. Approximation ratio = 1.0 "
                "(guaranteed optimal). Time complexity O(E log E)."
            ),
            meta     = meta,
            warnings = warnings,
        )

    # ══════════════════════════════════════════════════════
    # STEP 4 — SCHEDULING PROBLEM
    # ══════════════════════════════════════════════════════

    if problem_type == "scheduling":
        meta = ALGORITHM_REGISTRY["weighted_interval_scheduling_dp"]
        if n > meta["thresholds"]["max_n"]:
            raise ValueError(
                f"n={n} exceeds the maximum supported size "
                f"({meta['thresholds']['max_n']:,}) for scheduling DP. "
                "No feasible algorithm is available."
            )
        return _build_result(
            algorithm_name = "weighted_interval_scheduling_dp",
            justification  = (
                "Dynamic Programming (Weighted Interval Scheduling) selected. "
                "This DP approach finds the optimal non-overlapping set of "
                "intervals in O(n log n) time by sorting intervals by end "
                "time and using binary search to find compatible predecessors. "
                f"n={n} is within the threshold of {meta['thresholds']['max_n']:,}."
            ),
            meta     = meta,
            warnings = warnings,
        )

    # ══════════════════════════════════════════════════════
    # STEP 5 — SEQUENCE ALIGNMENT
    # ══════════════════════════════════════════════════════

    if problem_type == "sequence_alignment":
        meta = ALGORITHM_REGISTRY["sequence_alignment_dp"]
        if n > meta["thresholds"]["max_n"]:
            raise ValueError(
                f"n={n} exceeds the DP table limit "
                f"({meta['thresholds']['max_n']:,}) for sequence alignment. "
                "Consider a heuristic approach for very long sequences."
            )
        return _build_result(
            algorithm_name = "sequence_alignment_dp",
            justification  = (
                "Dynamic Programming (Sequence Alignment) selected. "
                "Edit distance between two sequences is solved exactly "
                "using the Needleman-Wunsch DP approach in O(n × m) time. "
                "The DP table stores minimum alignment cost for every "
                f"prefix pair. n={n} is within the threshold of "
                f"{meta['thresholds']['max_n']:,}."
            ),
            meta     = meta,
            warnings = warnings,
        )

    # ══════════════════════════════════════════════════════
    # STEP 6 — SHORTEST PATH
    # ══════════════════════════════════════════════════════

    if problem_type == "shortest_path":
        has_neg = kwargs.get("has_negative_weights", False)

        if has_neg:
            # Negative weights → MUST use Bellman-Ford
            meta = ALGORITHM_REGISTRY["bellman_ford_dp"]
            if n > meta["thresholds"]["max_n"]:
                raise ValueError(
                    f"n={n} exceeds Bellman-Ford's limit "
                    f"({meta['thresholds']['max_n']}) for graphs with "
                    "negative weights. No feasible exact algorithm available."
                )
            warnings.append(
                ALGORITHM_REGISTRY["bellman_ford_dp"]["warning"]
            )
            return _build_result(
                algorithm_name = "bellman_ford_dp",
                justification  = (
                    "Dynamic Programming (Bellman-Ford) selected. "
                    "Negative edge weights are present — Dijkstra is "
                    "INVALID in this case. Bellman-Ford correctly handles "
                    "negative weights by relaxing all edges (n-1) times "
                    "and detects negative-weight cycles. "
                    f"n={n} is within the limit of {meta['thresholds']['max_n']}."
                ),
                meta     = meta,
                warnings = warnings,
            )
        else:
            # No negative weights → Dijkstra
            meta = ALGORITHM_REGISTRY["dijkstra_greedy"]
            if n > meta["thresholds"]["max_n"]:
                # Fall back to Bellman-Ford if n is too large for Dijkstra
                warnings.append(
                    f"n={n} exceeds Dijkstra's simple limit "
                    f"({meta['thresholds']['max_n']}). "
                    "Falling back to Bellman-Ford."
                )
                meta_bf = ALGORITHM_REGISTRY["bellman_ford_dp"]
                return _build_result(
                    algorithm_name = "bellman_ford_dp",
                    justification  = (
                        "Dynamic Programming (Bellman-Ford) selected as fallback. "
                        f"n={n} exceeds Dijkstra's threshold. "
                        "Bellman-Ford handles larger graphs at the cost of "
                        "higher time complexity O(n × E)."
                    ),
                    meta     = meta_bf,
                    warnings = warnings,
                )
            warnings.append(meta["warning"])
            return _build_result(
                algorithm_name = "dijkstra_greedy",
                justification  = (
                    "Greedy (Dijkstra) selected. "
                    "No negative edge weights detected — Dijkstra's greedy "
                    "algorithm is provably optimal here. It always expands "
                    "the closest unvisited node first, guaranteeing shortest "
                    f"paths in O(n²) time. n={n} is within the limit of "
                    f"{meta['thresholds']['max_n']:,}."
                ),
                meta     = meta,
                warnings = warnings,
            )

    # ══════════════════════════════════════════════════════
    # STEP 7 — KNAPSACK & SUBSET PROBLEMS
    # ══════════════════════════════════════════════════════

    if problem_type == "subset":
        meta = ALGORITHM_REGISTRY["subset_bruteforce"]
        if n > meta["thresholds"]["max_n"]:
            raise ValueError(
                f"n={n} exceeds brute force limit ({meta['thresholds']['max_n']}) "
                "for subset enumeration. Exponential time complexity O(2^n) "
                "makes this infeasible for larger n."
            )
        return _build_result(
            algorithm_name = "subset_bruteforce",
            justification  = (
                f"Brute Force (Subset Enumeration) selected. For n={n}, "
                f"it is feasible to evaluate all 2^{n} = {2**n:,} possible "
                "subsets. This ensures we find the exact optimal subset "
                "based on the provided constraints."
            ),
            meta     = meta,
            warnings = warnings,
        )

    if problem_type in ("knapsack", "fractional_knapsack"):

        # ── 7a. Fractional knapsack → always greedy ────────
        if problem_type == "fractional_knapsack":
            meta = ALGORITHM_REGISTRY["fractional_knapsack_greedy"]
            return _build_result(
                algorithm_name = "fractional_knapsack_greedy",
                justification  = (
                    "Greedy (Fractional Knapsack) selected. "
                    "Items can be split (fractional variant), so the greedy "
                    "strategy of always taking the item with the highest "
                    "value-per-weight ratio is PROVABLY OPTIMAL. "
                    "Approximation ratio = 1.0. Time complexity O(n log n)."
                ),
                meta     = meta,
                warnings = warnings,
            )

        # ── 7b. Approximate or very tight time budget → Greedy ─
        if quality_requirement in ("approximate", "best_effort") or time_budget_ms < 100:
            meta = ALGORITHM_REGISTRY["fractional_knapsack_greedy"]
            if quality_requirement in ("approximate", "best_effort"):
                reason = (
                    f"quality_requirement='{quality_requirement}' — "
                    "exact solution not required."
                )
            else:
                reason = (
                    f"time_budget_ms={time_budget_ms} ms is very tight (<100 ms) — "
                    "only a fast greedy approach fits within the budget."
                )
            warnings.append(
                "Fractional Knapsack greedy used as approximation. "
                "Note: this solves the fractional relaxation. "
                "The 0/1 optimal may be higher."
            )
            return _build_result(
                algorithm_name = "fractional_knapsack_greedy",
                justification  = (
                    f"Greedy (Fractional Knapsack) selected. {reason} "
                    "The greedy approach runs in O(n log n) and provides "
                    "an approximate solution quickly. For the fractional "
                    "relaxation, this IS optimal (ratio=1.0). For the 0/1 "
                    "variant it serves as a fast upper-bound approximation."
                ),
                meta     = meta,
                warnings = warnings,
            )

        # ── 7c. Exact quality required ─────────────────────

        # Brute force: only when n is tiny (≤ 15)
        bf_meta = ALGORITHM_REGISTRY["knapsack_brute_force"]
        if n <= bf_meta["thresholds"]["max_n"]:
            warnings.append(bf_meta["warning"])
            return _build_result(
                algorithm_name = "knapsack_brute_force",
                justification  = (
                    f"Brute Force selected. n={n} ≤ 15, so exhaustive "
                    "enumeration of all 2^n subsets is feasible. "
                    "Brute force guarantees the exact optimal solution "
                    "and is used here to verify correctness. "
                    f"Total subsets to evaluate: {2**n:,}."
                ),
                meta     = bf_meta,
                warnings = warnings,
            )

        # DP: for larger n when memory threshold is met
        dp_meta   = ALGORITHM_REGISTRY["knapsack_dp"]
        capacity  = kwargs.get("capacity", None)

        if capacity is None:
            warnings.append(
                "capacity was not provided — assuming capacity=n*10 "
                "for threshold check. Pass capacity for accurate routing."
            )
            capacity = n * 10   # safe assumption for threshold check

        n_times_cap = n * capacity
        if (n <= dp_meta["thresholds"]["max_n"]
                and n_times_cap <= dp_meta["thresholds"]["max_n_times_capacity"]):
            return _build_result(
                algorithm_name = "knapsack_dp",
                justification  = (
                    "Dynamic Programming (0/1 Knapsack) selected. "
                    f"n={n} ≤ {dp_meta['thresholds']['max_n']} and "
                    f"n × capacity = {n_times_cap:,} ≤ "
                    f"{dp_meta['thresholds']['max_n_times_capacity']:,}. "
                    "DP builds an optimal table of size (n+1)×(capacity+1) "
                    "and backtracks to find the exact best subset. "
                    "Time complexity O(n × capacity), quality = 100% optimal."
                ),
                meta     = dp_meta,
                warnings = warnings,
            )

        # DP thresholds exceeded → warn and fall back to greedy
        warnings.append(
            f"DP thresholds exceeded (n={n}, n×capacity={n_times_cap:,}). "
            "Exact DP is infeasible. Falling back to Greedy approximation."
        )
        meta = ALGORITHM_REGISTRY["fractional_knapsack_greedy"]
        return _build_result(
            algorithm_name = "fractional_knapsack_greedy",
            justification  = (
                "Greedy (Fractional Knapsack) selected as fallback. "
                f"n={n} or n×capacity={n_times_cap:,} exceeds DP memory "
                "limits and brute force is infeasible for n>15. "
                "Greedy provides a fast approximate solution in O(n log n). "
                "For 0/1 knapsack this is an approximation (ratio may be <1.0)."
            ),
            meta     = meta,
            warnings = warnings,
        )

    # ══════════════════════════════════════════════════════
    # STEP 8 — SHOULD NEVER REACH HERE
    # ══════════════════════════════════════════════════════
    raise ValueError(
        f"No algorithm found for problem_type='{problem_type}'. "
        "This is an internal error — all valid problem types should "
        "have been handled above."
    )


# ╔══════════════════════════════════════════════════════════╗
# ║              PRIVATE HELPER: _build_result               ║
# ╚══════════════════════════════════════════════════════════╝

def _build_result(
    algorithm_name: str,
    justification: str,
    meta: dict,
    warnings: list,
) -> dict:
    """
    Packages the decision into the standard output format.
    Called internally by choose_algorithm().

    Args:
        algorithm_name : canonical name from ALGORITHM_REGISTRY
        justification  : explanation paragraph
        meta           : the full ALGORITHM_REGISTRY entry
        warnings       : list of warning strings

    Returns:
        dict matching the format Member 3 expects
    """
    # Map quality → human-readable guarantee label
    quality_labels = {
        "exact"      : "100% optimal (exact solution guaranteed)",
        "approximate": "Approximate (provably bounded approximation ratio)",
        "heuristic"  : "Heuristic (no formal guarantee)",
    }
    quality_guarantee = quality_labels.get(meta["quality"], meta["quality"])

    # Filter out None warnings (some registry entries have warning=None)
    clean_warnings = [w for w in warnings if w is not None]

    return {
        "algorithm_name"    : algorithm_name,
        "justification"     : justification,
        "expected_complexity": meta["time_complexity"],
        "space_complexity": meta["space_complexity"],
        "quality_guarantee" : quality_guarantee,
        "warnings"          : clean_warnings,
    }


# ╔══════════════════════════════════════════════════════════╗
# ║                    TEST CASES                            ║
# ╚══════════════════════════════════════════════════════════╝

if __name__ == "__main__":

    def print_decision(label: str, decision: dict) -> None:
        """Helper to print a decision result clearly."""
        print(f"\n{'='*60}")
        print(f"TEST: {label}")
        print(f"{'='*60}")
        print(f"  Algorithm   : {decision['algorithm_name']}")
        print(f"  Complexity  : {decision['expected_complexity']}")
        print(f"  Quality     : {decision['quality_guarantee']}")
        print(f"  Justification:")
        # Word-wrap the justification for readability
        words = decision["justification"].split()
        line  = "    "
        for word in words:
            if len(line) + len(word) > 72:
                print(line)
                line = "    " + word + " "
            else:
                line += word + " "
        print(line)
        if decision["warnings"]:
            print(f"  Warnings:")
            for w in decision["warnings"]:
                print(f"    ⚠  {w}")

    # ── Test 1: Knapsack n=3, exact → Brute Force ──────────
    print_decision(
        "Knapsack n=3, exact → should pick Brute Force",
        choose_algorithm("knapsack", n=3, time_budget_ms=500,
                         quality_requirement="exact", capacity=50)
    )

    # ── Test 2: Knapsack n=20, exact, capacity=100 → DP ───
    print_decision(
        "Knapsack n=20, exact, capacity=100 → should pick DP",
        choose_algorithm("knapsack", n=20, time_budget_ms=500,
                         quality_requirement="exact", capacity=100)
    )

    # ── Test 3: Knapsack n=20, approximate → Greedy ────────
    print_decision(
        "Knapsack n=20, approximate → should pick Greedy",
        choose_algorithm("knapsack", n=20, time_budget_ms=500,
                         quality_requirement="approximate", capacity=100)
    )

    # ── Test 4: Sorting → Merge Sort ───────────────────────
    print_decision(
        "Sorting → should pick Merge Sort",
        choose_algorithm("sorting", n=1000, time_budget_ms=1000,
                         quality_requirement="exact")
    )

    # ── Test 5: Shortest path, negative weights → Bellman-Ford
    print_decision(
        "Shortest path with negative weights → should pick Bellman-Ford",
        choose_algorithm("shortest_path", n=10, time_budget_ms=500,
                         quality_requirement="exact",
                         has_negative_weights=True)
    )

    # ── Test 6: Shortest path, no negative weights → Dijkstra
    print_decision(
        "Shortest path, no negative weights → should pick Dijkstra",
        choose_algorithm("shortest_path", n=10, time_budget_ms=500,
                         quality_requirement="exact",
                         has_negative_weights=False)
    )

    # ── Test 7: MST → Kruskal ──────────────────────────────
    print_decision(
        "MST → should pick Kruskal",
        choose_algorithm("mst", n=100, time_budget_ms=500,
                         quality_requirement="exact")
    )

    # ── Test 8: Searching, sorted → Binary Search ──────────
    print_decision(
        "Searching (sorted array) → should pick Binary Search",
        choose_algorithm("searching", n=1000, time_budget_ms=500,
                         quality_requirement="exact", is_sorted=True)
    )

    # ── Test 9: Searching, unsorted → should raise error ───
    print(f"\n{'='*60}")
    print("TEST: Searching on unsorted array → should raise ValueError")
    print(f"{'='*60}")
    try:
        choose_algorithm("searching", n=100, time_budget_ms=500,
                         quality_requirement="exact", is_sorted=False)
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")

    # ── Test 10: n=0 → should raise error ──────────────────
    print(f"\n{'='*60}")
    print("TEST: n=0 → should raise ValueError")
    print(f"{'='*60}")
    try:
        choose_algorithm("knapsack", n=0, time_budget_ms=500,
                         quality_requirement="exact")
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")

    # ── Test 11: Tight time budget → Greedy ────────────────
    print_decision(
        "Knapsack, time_budget_ms=50 (tight) → should pick Greedy",
        choose_algorithm("knapsack", n=20, time_budget_ms=50,
                         quality_requirement="exact", capacity=100)
    )

    # ── Test 12: Exponentiation → Fast Exp ─────────────────
    print_decision(
        "Exponentiation → should pick Fast Exponentiation",
        choose_algorithm("exponentiation", n=1000000, time_budget_ms=500,
                         quality_requirement="exact")
    )

    # ── Test 13: Sequence Alignment → DP ───────────────────
    print_decision(
        "Sequence Alignment → should pick Sequence Alignment DP",
        choose_algorithm("sequence_alignment", n=100, time_budget_ms=500,
                         quality_requirement="exact")
    )

    # ── Test 14: Scheduling → Weighted Interval Scheduling ─
    print_decision(
        "Scheduling → should pick Weighted Interval Scheduling DP",
        choose_algorithm("scheduling", n=500, time_budget_ms=500,
                         quality_requirement="exact")
    )

    # ── Test 15: Fractional Knapsack → Greedy (always) ─────
    print_decision(
        "Fractional Knapsack → should always pick Greedy",
        choose_algorithm("fractional_knapsack", n=100, time_budget_ms=500,
                         quality_requirement="exact")
    )

    print(f"\n{'='*60}")
    print("All tests completed.")
    print(f"{'='*60}\n")
