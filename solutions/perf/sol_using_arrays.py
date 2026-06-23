"""Solution for the "Using Arrays" exercise.

Derive a column-wise dataframe class that uses Python's array.array for
numeric storage.  Arrays are more compact than lists and can be faster
for numeric operations, though they only store homogeneous primitive
types.
"""

import time
from array import array
from df_base import DataFrame
from util import all_eq


class DfArray(DataFrame):
    """Column-wise dataframe backed by array.array for each column."""

    def __init__(self, **kwargs):
        """kwargs maps column names to lists (converted to arrays)."""
        assert len(kwargs) > 0
        lengths = [len(v) for v in kwargs.values()]
        assert all_eq(*lengths)
        self._data = {}
        for k in kwargs:
            vals = kwargs[k]
            # Pick array typecode from the first element's type.
            if isinstance(vals[0], int):
                self._data[k] = array("i", vals)
            elif isinstance(vals[0], float):
                self._data[k] = array("d", vals)
            else:
                self._data[k] = list(vals)
        self._nrow = lengths[0]

    def ncol(self):
        return len(self._data)

    def nrow(self):
        return self._nrow

    def cols(self):
        return set(self._data.keys())

    def get(self, col, row):
        assert col in self._data
        assert 0 <= row < self._nrow
        return self._data[col][row]

    def eq(self, other):
        assert isinstance(other, DataFrame)
        for n in self._data:
            if n not in other.cols():
                return False
            for i in range(self._nrow):
                if self.get(n, i) != other.get(n, i):
                    return False
        return True

    def select(self, *names):
        assert all(n in self._data for n in names)
        return DfArray(**{n: self._data[n] for n in names})

    def filter(self, func):
        result = {n: [] for n in self._data}
        for i in range(self._nrow):
            args = {n: self._data[n][i] for n in self._data}
            if func(**args):
                for n in self._data:
                    result[n].append(self._data[n][i])
        return DfArray(**result)

    def __str__(self):
        return str({k: list(v) for k, v in self._data.items()})


# ---------------------------------------------------------------------------
# Benchmark against DfCol
# ---------------------------------------------------------------------------

RANGE = 10


def make_col(nrow, ncol):
    def _col(n, start):
        return [((start + i) % RANGE) for i in range(n)]

    return {f"label_{c}": _col(nrow, c) for c in range(ncol)}


if __name__ == "__main__":
    from df_col import DfCol

    nrow, ncol = 2000, 30
    fill = make_col(nrow, ncol)

    df_col = DfCol(**fill)
    df_arr = DfArray(**fill)

    def filt(label_0, **kwargs):
        return label_0 % 2 == 1

    t0 = time.time()
    df_col.filter(filt)
    t_col = time.time() - t0

    t0 = time.time()
    df_arr.filter(filt)
    t_arr = time.time() - t0

    print(f"DfCol  filter: {t_col:.6f} s")
    print(f"DfArray filter: {t_arr:.6f} s")
    print()
    print(
        "array.array stores values in a contiguous C array, which can "
        "reduce memory overhead and improve cache locality for numeric "
        "data.  The speedup is most noticeable with large integer or "
        "float columns where the typecode can be inferred automatically."
    )
