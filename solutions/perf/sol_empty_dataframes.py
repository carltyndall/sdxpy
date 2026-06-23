"""Solution for the "Empty Dataframes" exercise.

Derive a row-wise dataframe class from DataFrame that can represent a
dataframe with no rows.  The trick is to store column names separately
instead of relying on the first row to supply them.
"""

from df_base import DataFrame
from util import dict_match


class DfRowEmpty(DataFrame):
    """Row-wise dataframe that supports zero-row construction."""

    def __init__(self, rows, cols=None):
        """Create a row-wise dataframe.

        rows : list[dict]   -- the data rows (may be empty).
        cols : list[str]    -- column names; required when rows is empty.
        """
        if not rows:
            assert cols is not None, "must supply cols for an empty dataframe"
            self._cols = list(cols)
            self._data = []
        else:
            assert all(dict_match(r, rows[0]) for r in rows)
            self._cols = list(rows[0].keys())
            self._data = rows

    def ncol(self):
        return len(self._cols)

    def nrow(self):
        return len(self._data)

    def cols(self):
        return set(self._cols)

    def get(self, col, row):
        assert col in self._cols
        assert 0 <= row < len(self._data)
        return self._data[row][col]

    def eq(self, other):
        assert isinstance(other, DataFrame)
        if self.ncol() != other.ncol() or self.nrow() != other.nrow():
            return False
        for c in self._cols:
            if c not in other.cols():
                return False
            for i in range(self.nrow()):
                if self.get(c, i) != other.get(c, i):
                    return False
        return True

    def select(self, *names):
        assert all(n in self._cols for n in names)
        rows = [{key: r[key] for key in names} for r in self._data]
        return DfRowEmpty(rows, cols=list(names))

    def filter(self, func):
        result = [r for r in self._data if func(**r)]
        return DfRowEmpty(result, cols=self._cols)

    def __str__(self):
        return str(self._data)


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Empty dataframe with known columns.
    empty = DfRowEmpty([], cols=["a", "b"])
    print(f"Empty: nrow={empty.nrow()}, ncol={empty.ncol()}, cols={empty.cols()}")
    assert empty.nrow() == 0
    assert empty.ncol() == 2

    # Non-empty dataframe works as before.
    full = DfRowEmpty([{"a": 1, "b": 3}, {"a": 2, "b": 4}])
    print(f"Full:  nrow={full.nrow()}, ncol={full.ncol()}, cols={full.cols()}")
    assert full.get("a", 0) == 1

    # Filtering works and can produce an empty result.
    def never(a, b):
        return False

    filtered = full.filter(never)
    print(f"Filtered: nrow={filtered.nrow()}, cols={filtered.cols()}")
    assert filtered.nrow() == 0
    print("All assertions passed.")
