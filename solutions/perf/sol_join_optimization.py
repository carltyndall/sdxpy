"""Solution for the "Join Optimization" exercise.

Implement an index-based join that builds a lookup map from key to row
indices for each table, then constructs matches from the smaller map.
Compare its performance to the naive double-loop join.
"""

import random
import time
from df_col import DfCol
from df_row import DfRow


# --- Index construction ---

def build_index(df, on):
    """Return a dict mapping each key value to a list of row indices."""
    idx = {}
    n = df.nrow()
    for i in range(n):
        key = df.get(on, i)
        idx.setdefault(key, []).append(i)
    return idx


# --- Index-based join ---

def join_indexed(left, right, on):
    """Inner join using a pre-built index on the smaller table."""
    idx = build_index(left if left.nrow() <= right.nrow() else right, on)
    # We'll always iterate over 'other' and probe 'idx'.
    if left.nrow() <= right.nrow():
        probe, other = idx, right
        probe_is_left = True
    else:
        probe, other = idx, left
        probe_is_left = False

    if probe_is_left:
        # probe = left index, other = right
        result = []
        for j in range(other.nrow()):
            rkey = other.get(on, j)
            if rkey in probe:
                for i in probe[rkey]:
                    merged = {c: left.get(c, i) for c in left.cols()}
                    for c in right.cols():
                        if c != on:
                            merged[c] = right.get(c, j)
                    result.append(merged)
        return DfRow(result)
    else:
        # probe = right index, other = left
        result = []
        for i in range(other.nrow()):
            lkey = other.get(on, i)
            if lkey in probe:
                for j in probe[lkey]:
                    merged = {c: other.get(c, i) for c in other.cols()}
                    for c in right.cols():
                        if c != on:
                            merged[c] = right.get(c, j)
                    result.append(merged)
        return DfRow(result)


# --- Naive join for comparison ---

def join_naive(left, right, on):
    """Double-loop inner join (always returns DfRow)."""
    result = []
    for i in range(left.nrow()):
        lkey = left.get(on, i)
        for j in range(right.nrow()):
            if right.get(on, j) == lkey:
                merged = {c: left.get(c, i) for c in left.cols()}
                for c in right.cols():
                    if c != on:
                        merged[c] = right.get(c, j)
                result.append(merged)
    return DfRow(result)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_row(nrow, key_space):
    rows = [{"Key": random.randint(0, key_space - 1), "Left": f"l{i}"}
            for i in range(nrow)]
    return DfRow(rows)


def make_col(nrow, key_space):
    keys = [random.randint(0, key_space - 1) for _ in range(nrow)]
    vals = [f"r{i}" for i in range(nrow)]
    return DfCol(Key=keys, Right=vals)


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(99)
    sizes = [(200, 200), (200, 50), (200, 5)]
    print(f"{'key_space':>10} {'naive(s)':>12} {'index(s)':>12}")
    print("-" * 38)
    for key_space in sizes:
        left = make_row(200, key_space[0])
        right = make_col(200, key_space[1])

        t0 = time.time()
        join_naive(left, right, "Key")
        t_naive = time.time() - t0

        t0 = time.time()
        join_indexed(left, right, "Key")
        t_index = time.time() - t0

        print(f"  {key_space[0]:>4}/{key_space[1]:<4}  {t_naive:>12.6f} {t_index:>12.6f}")

    print()
    print(
        "The index-based join is O(n + m + k) where n and m are the "
        "table sizes and k is the number of matching pairs produced. "
        "The double-loop join is always O(n × m).  When key spaces are "
        "large (few collisions), the index join is dramatically faster. "
        "When the key space is tiny (many collisions, large output), "
        "both approaches converge because the output construction "
        "dominates the cost."
    )
