"""Solution for the "Conversion" exercise.

Write conversion functions between DfRow and DfCol and benchmark them
to see which direction is faster and how the difference scales.
"""

import time
from df_col import DfCol
from df_row import DfRow


def dfrow_to_dfcol(df_row):
    """Convert a DfRow to a DfCol."""
    cols = df_row.cols()
    n = df_row.nrow()
    return DfCol(**{c: [df_row.get(c, i) for i in range(n)] for c in cols})


def dfcol_to_dfrow(df_col):
    """Convert a DfCol to a DfRow."""
    cols = list(df_col.cols())
    n = df_col.nrow()
    rows = [{c: df_col.get(c, i) for c in cols} for i in range(n)]
    return DfRow(rows)


# ---------------------------------------------------------------------------
# Helpers for building test data
# ---------------------------------------------------------------------------

RANGE = 10


def make_row(nrow, ncol):
    labels = [f"label_{c}" for c in range(ncol)]

    def _row(r):
        return {c: ((r + i) % RANGE) for (i, c) in enumerate(labels)}

    return DfRow([_row(r) for r in range(nrow)])


def make_col(nrow, ncol):
    def _col(n, start):
        return [((start + i) % RANGE) for i in range(n)]

    return DfCol(**{f"label_{c}": _col(nrow, c) for c in range(ncol)})


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for nrow, ncol in [(200, 10), (500, 50), (1000, 100)]:
        df_row = make_row(nrow, ncol)
        df_col = make_col(nrow, ncol)

        t0 = time.time()
        dfrow_to_dfcol(df_row)
        t_row2col = time.time() - t0

        t0 = time.time()
        dfcol_to_dfrow(df_col)
        t_col2row = time.time() - t0

        print(f"{nrow}x{ncol}:"
              f" row→col {t_row2col:.6f}s"
              f" | col→row {t_col2row:.6f}s")
    print()
    print(
        "Row→col conversion iterates over every cell to repack values "
        "from dictionaries into per-column lists.  Col→row does the "
        "reverse.  Both are O(nrow × ncol), but col→row is usually "
        "faster in Python because building many small dicts has more "
        "overhead than building lists via comprehension.  The gap "
        "widens as the dataframe gets wider (more keys per dict)."
    )
