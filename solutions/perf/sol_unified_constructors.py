"""Solution for the "Unified Constructors" exercise.

Give DfRow and DfCol constructors the same signature.  We choose the
column-wise kwargs style (col_name=list_of_values) as the common
interface because it naturally represents the schema and works for
both storage layouts.
"""

from df_base import DataFrame
from util import dict_match, all_eq


class DfRowUnified(DataFrame):
    """Row-wise dataframe whose constructor matches DfCol's kwargs style."""

    def __init__(self, **kwargs):
        """kwargs maps column names to lists of values (all same length)."""
        assert len(kwargs) > 0
        lengths = [len(v) for v in kwargs.values()]
        assert all_eq(*lengths)
        for k in kwargs:
            assert all_eq(type(v) for v in kwargs[k])
        self._cols = list(kwargs.keys())
        n = lengths[0]
        self._data = [{c: kwargs[c][i] for c in self._cols} for i in range(n)]

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
        for i, row in enumerate(self._data):
            for key in row:
                if key not in other.cols():
                    return False
                if row[key] != other.get(key, i):
                    return False
        return True

    def select(self, *names):
        assert all(n in self._cols for n in names)
        rows = [{key: r[key] for key in names} for r in self._data]
        return DfRowUnified(**{n: [r[n] for r in rows] for n in names})

    def filter(self, func):
        result = [r for r in self._data if func(**r)]
        return DfRowUnified(**{c: [r[c] for r in result] for c in self._cols})

    def __str__(self):
        return str(self._data)


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Both classes now use the same constructor style.
    from df_col import DfCol

    row_df = DfRowUnified(a=[1, 2], b=[3, 4])
    col_df = DfCol(a=[1, 2], b=[3, 4])

    assert row_df.eq(col_df)
    assert col_df.eq(row_df)
    print("Unified constructors: both DfRowUnified and DfCol accept **kwargs.")
    print("This is useful when a factory function needs to create either")
    print("storage layout without knowing which one at the call site —")
    print("you can pass the class as a parameter and the same arguments.")
