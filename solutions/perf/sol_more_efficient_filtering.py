"""Solution for the "More Efficient Filtering" exercise.

Derive a class from DfCol that overrides filter so the user-defined function
receives a row index i_row plus only the columns it asks for (via inspect).
"""

import inspect
import time
from df_col import DfCol


class DfColIndexed(DfCol):
    """Column-wise dataframe where filter functions can accept i_row
    and only the columns they need."""

    def filter(self, func):
        sig = inspect.signature(func)
        param_names = set(sig.parameters.keys())
        result = {n: [] for n in self._data}
        for i in range(self.nrow()):
            kwargs = {}
            if "i_row" in param_names:
                kwargs["i_row"] = i
            for n in self._data:
                if n in param_names:
                    kwargs[n] = self._data[n][i]
            if func(**kwargs):
                for n in self._data:
                    result[n].append(self._data[n][i])
        return DfCol(**result)


# ---------------------------------------------------------------------------
# Demonstration and timing
# ---------------------------------------------------------------------------

RANGE = 10


def make_col(nrow, ncol):
    def _col(n, start):
        return [((start + i) % RANGE) for i in range(n)]

    fill = {f"label_{c}": _col(nrow, c) for c in range(ncol)}
    return DfCol(**fill)


def time_filter(cls, df, func):
    start = time.time()
    df.filter(func)
    return time.time() - start


if __name__ == "__main__":
    # Build a moderate-sized dataframe.
    nrow, ncol = 1000, 20
    df = make_col(nrow, ncol)

    # --- Original DfCol.filter: must accept every column ---
    def old_filter(**kwargs):
        return kwargs["label_0"] % 2 == 1

    t_old = time_filter(DfCol, df, old_filter)

    # --- Indexed variant: only label_0 is needed ---
    def idx_filter(label_0, i_row):
        return label_0 % 2 == 1

    df_idx = DfColIndexed(**df._data)
    t_idx = time_filter(DfColIndexed, df_idx, idx_filter)

    # --- Indexed variant using only i_row (keep every 10th row) ---
    def row_only(i_row):
        return i_row % 10 == 0

    t_row = time_filter(DfColIndexed, df_idx, row_only)

    print(f"Original DfCol.filter : {t_old:.6f} s")
    print(f"Indexed  (label_0)    : {t_idx:.6f} s")
    print(f"Indexed  (i_row only) : {t_row:.6f} s")
    print()
    print(
        "When the filter function only needs i_row (no columns), "
        "we skip building the per-row dictionary entirely, "
        "which can be a substantial win for wide tables.  "
        "Row-index-only filtering is useful for subsampling "
        "(e.g. keep every Nth row) or for implementing "
        "train/test splits without touching column data."
    )
