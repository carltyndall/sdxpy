"""Solution for the "Crossover" exercise.

Find the ratio of filter-to-select operations at which DfRow and DfCol
perform equally, and explore how relative performance changes when the
number of columns is fixed but rows increase.
"""

import time
from df_col import DfCol
from df_row import DfRow

RANGE = 10
FILTER_MOD = 2
SELECT_MOD = 3


def make_col(nrow, ncol):
    def _col(n, start):
        return [((start + i) % RANGE) for i in range(n)]

    return DfCol(**{f"label_{c}": _col(nrow, c) for c in range(ncol)})


def make_row(nrow, ncol):
    labels = [f"label_{c}" for c in range(ncol)]

    def _row(r):
        return {c: ((r + i) % RANGE) for (i, c) in enumerate(labels)}

    return DfRow([_row(r) for r in range(nrow)])


def time_filter(df):
    def f(label_0, **args):
        return label_0 % FILTER_MOD == 1

    start = time.time()
    df.filter(f)
    return time.time() - start


def time_select(df):
    indices = [i for i in range(df.ncol()) if ((i % SELECT_MOD) == 0)]
    labels = [f"label_{i}" for i in indices]
    start = time.time()
    df.select(*labels)
    return time.time() - start


def weighted_time(df, pct_filter):
    """Return weighted average time for a mix of filter and select ops."""
    t_f = time_filter(df)
    t_s = time_select(df)
    return pct_filter * t_f + (1.0 - pct_filter) * t_s


def find_crossover(nrow, ncol):
    """Binary-search the filter fraction where row and col times match."""
    df_row = make_row(nrow, ncol)
    df_col = make_col(nrow, ncol)
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        tr = weighted_time(df_row, mid)
        tc = weighted_time(df_col, mid)
        if tr < tc:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


if __name__ == "__main__":
    # --- Part 1: crossover at a few sizes ---
    print("=== Part 1: crossover ratio (filter fraction) ===\n")
    for nrow, ncol in [(200, 10), (500, 20), (1000, 50)]:
        ratio = find_crossover(nrow, ncol)
        print(
            f"  {nrow}x{ncol}: DfRow≈DfCol when ~{ratio:.1%} of ops are filters"
        )

    # --- Part 2: fixed columns, growing rows ---
    print("\n=== Part 2: fixed columns (10), growing rows ===\n")
    for nrow in [100, 500, 2000]:
        df_row = make_row(nrow, 10)
        df_col = make_col(nrow, 10)
        t_rf = time_filter(df_row)
        t_cf = time_filter(df_col)
        t_rs = time_select(df_row)
        t_cs = time_select(df_col)
        print(f"  {nrow}x10 rows:"
              f" filter row={t_rf:.6f}s col={t_cf:.6f}s"
              f" | select row={t_rs:.6f}s col={t_cs:.6f}s")
    print()
    print(
        "With a fixed number of columns, row-wise select gets linearly "
        "more expensive as rows grow (we must visit every row to pluck "
        "out the column values), whereas column-wise select simply "
        "returns references to existing column lists.  Filter times "
        "grow similarly for both layouts.  Fixed-column / growing-row "
        "is the more realistic scenario for most analytics workloads."
    )
