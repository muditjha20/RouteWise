# src/algorithms.py
import math
from typing import List, Tuple
import numpy as np
from itertools import combinations

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def build_distance_matrix(coords: List[Tuple[float, float, str]]) -> np.ndarray:
    n = len(coords)
    mat = np.zeros((n, n), dtype=float)
    for i in range(n):
        lat1, lon1, _ = coords[i]
        for j in range(i + 1, n):
            lat2, lon2, _ = coords[j]
            d = haversine_m(lat1, lon1, lat2, lon2)
            mat[i, j] = mat[j, i] = d
    return mat

def held_karp_loop(dist: np.ndarray) -> Tuple[List[int], float]:
    """
    Optimal TSP loop with start=end=0.
    Returns (route_indices including final 0, total_distance_m).
    """
    n = dist.shape[0]
    if n == 1:
        return [0, 0], 0.0
    if n == 2:
        total = dist[0,1] + dist[1,0]
        return [0,1,0], total

    # dp[(mask, j)] = best cost to reach j having visited exactly 'mask' (includes 0 and j)
    # parent[(mask, j)] = predecessor node i
    dp = {}
    parent = {}

    # Subsets are built by increasing size to ensure dependencies are ready.
    # Initialize all subsets of size 2 (0 and j).
    for j in range(1, n):
        mask = (1 << 0) | (1 << j)
        dp[(mask, j)] = dist[0, j]
        parent[(mask, j)] = 0

    # Grow subset sizes from 3..n
    all_nodes_except_start = list(range(1, n))
    for size in range(3, n + 1):
        for subset in combinations(all_nodes_except_start, size - 1):
            # Build bitmask for subset U {0}
            mask = 1  # include node 0
            for v in subset:
                mask |= (1 << v)

            # For each possible end j in subset
            for j in subset:
                best = math.inf
                best_i = -1
                prev_mask = mask ^ (1 << j)
                # try all predecessors i in subset \ {j}
                for i in subset:
                    if i == j:
                        continue
                    cand_key = (prev_mask, i)
                    if cand_key not in dp:
                        continue
                    cost = dp[cand_key] + dist[i, j]
                    if cost < best:
                        best = cost
                        best_i = i
                if best_i != -1:
                    dp[(mask, j)] = best
                    parent[(mask, j)] = best_i

    # Close the tour back to 0
    full_mask = (1 << n) - 1
    best_total = math.inf
    best_end = -1
    for j in range(1, n):
        key = (full_mask, j)
        if key in dp:
            total = dp[key] + dist[j, 0]
            if total < best_total:
                best_total = total
                best_end = j

    # Reconstruct route
    if best_end == -1:
        # Shouldn't happen; fallback to trivial order
        return list(range(n)) + [0], float("inf")

    route = [0] * (n + 1)
    route[-1] = 0
    mask = full_mask
    j = best_end
    for k in range(n - 1, 0, -1):
        route[k] = j
        i = parent[(mask, j)]
        mask ^= (1 << j)
        j = i
    route[0] = 0
    return route, best_total
