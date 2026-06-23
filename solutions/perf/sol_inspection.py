"""Solution for the "Inspection" exercise.

Rewrite DfCol.filter using Python's inspect module so that filter
functions only need to accept parameters for the columns they actually
use.  This avoids the requirement that the function accept every column
in the dataframe.
"""

import inspect
import time
from df_col import DfCol


class DfColInspect(DfCol):
    """Column-wise dataframe whose filter method uses inspect to
    determine which columns the user's function needs."""

    def filter(self, func):
        sig = inspect.signature(func)
        param_names = set(sig.parameters.keys())
        result = {n: [] for n in self._data}
        data = self._data
        n = self.nrow()
        for i in range(n):
            # Build kwargs from only the columns the function asks for.
            kwargs = {p: data[p][i] for p in param_names if p in data}
            if func(**kwargs):
                for col in data:
                    result[col].append(data[col][i])
        return DfCol(**result)


# ---------------------------------------------------------------------------
# Demonstration and timing
# ---------------------------------------------------------------------------

RANGE = 10


def make_col(nrow, ncol):
    def _col(n, start):
        return [((start + i) % RANGE) for i in range(n)]

    return DfCol(**{f"label_{c}": _col(nrow, c) for c in range(ncol)})


if __name__ == "__main__":
    nrow, ncol = 1000, 30
    df = make_col(nrow, ncol)
    dfi = DfColInspect(**df._data)

    # Old-style: must list every column (or use **kwargs).
    def old_filter(label_0, **kwargs):
        return label_0 % 2 == 1

    t0 = time.time()
    df.filter(old_filter)
    t_old = time.time() - t0

    # New-style: only declare the columns you need.
    def new_filter(label_0):
        return label_0 % 2 == 1

    t0 = time.time()
    dfi.filter(new_filter)
    t_new = time.time() - t0

    print(f"nrow={nrow}, ncol={ncol}")
    print(f"  DfCol.filter  (**kwargs) : {t_old:.6f} s")
    print(f"  DfColInspect.filter       : {t_new:.6f} s")
    print()
    print(
        "Using inspect lets the user write filter functions that only "
        "name the columns they care about.  Internally we build a "
        "smaller kwargs dict (only requested columns), which reduces "
        "overhead for wide tables.  The speedup grows with the ratio "
        "of total columns to columns actually used in the predicate."
    )
