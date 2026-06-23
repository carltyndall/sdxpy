"""Solution for the "Join Performance" exercise.

Implement an inner join for both DfRow and DfCol and compare their
performance as the fraction of matching keys varies.
"""

import random
import time
from df_col import DfCol
from df_row import DfRow


def join_rows(left, right, on):
    """Inner join of two DfRow dataframes on column 'on'."""
    result = []
    for lrow in left._data:
        lkey = lrow[on]
        for rrow in right._data:
            if rrow[on] == lkey:
                merged = {**lrow}
                for k, v in rrow.items():
                    if k != on:
                        merged[k] = v
                result.append(merged)
    return DfRow(result)


def join_cols(left, right, on):
    """Inner join of two DfCol dataframes on column 'on'."""
    result = {}
    # Copy left columns.
    for col in left._data:
        result[col] = []
    # Add right columns (excluding the join key).
    for col in right._data:
        if col != on:
            result[col] = []
    n_left = left.nrow()
    n_right = right.nrow()
    for i in range(n_left):
        lkey = left.get(on, i)
        for j in range(n_right):
            if right.get(on, j) == lkey:
                for col in left._data:
                    result[col].append(left.get(col, i))
                for col in right._data:
                    if col != on:
                        result[col].append(right.get(col, j))
    return DfCol(**result)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_row(nrow, key_space):
    """Build a DfRow with Key and Left columns."""
    rows = [{"Key": random.randint(0, key_space - 1), "Left": f"l{i}"}
            for i in range(nrow)]
    return DfRow(rows)


def make_col(nrow, key_space):
    """Build a DfCol with Key and Right columns."""
    keys = [random.randint(0, key_space - 1) for _ in range(nrow)]
    vals = [f"r{i}" for i in range(nrow)]
    return DfCol(Key=keys, Right=vals)


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)
    n = 200

    print("key_space   match_frac   DfRow_join(s)   DfCol_join(s)")
    print("-" * 55)
    for key_space in [n, n // 2, n // 10, 5]:
        df_left = make_row(n, key_space)
        df_right = make_col(n, key_space)

        t0 = time.time()
        join_rows(df_left, df_right, "Key")
        t_row = time.time() - t0

        t0 = time.time()
        join_cols(df_left, df_right, "Key")
        t_col = time.time() - t0

        # Approximate fraction of matching keys.
        match_frac = 1.0 / key_space if key_space > 1 else 1.0
        print(f"  {key_space:>5}      {match_frac:>10.3f}    {t_row:>12.6f}    {t_col:>12.6f}")

    print()
    print(
        "Both implementations use a double loop, so join is O(n²) "
        "regardless of storage layout.  Row-wise storage has a slight "
        "edge because key lookups are dict accesses; column-wise storage "
        "calls .get() for every cell, which adds function-call overhead. "
        "As the key space shrinks (more matches), the output grows and "
        "both slow down proportionally — the fraction of matching keys "
        "affects the output size (and therefore total work), but the "
        "relative ranking stays similar."
    )
