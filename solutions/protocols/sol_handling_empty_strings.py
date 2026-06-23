"""Solution: iterator that correctly handles empty strings."""


class BetterIterator:
    """Store text lines and iterate over their characters."""

    def __init__(self, text):
        self._text = text[:]

    def __iter__(self):
        return BetterCursor(self._text)


class BetterCursor:
    """Cursor that yields characters from a list of strings.

    Empty strings are skipped entirely---they contribute no characters
    to the iteration.
    """

    def __init__(self, text):
        self._text = text
        self._row = 0
        self._col = -1

    def __next__(self):
        self._advance()
        if self._row == len(self._text):
            raise StopIteration
        return self._text[self._row][self._col]

    def _advance(self):
        """Move to the next non-empty character position."""
        while self._row < len(self._text):
            self._col += 1
            if self._col < len(self._text[self._row]):
                return  # found a character in the current row
            # End of current row: move to the next row.
            self._row += 1
            self._col = -1


# --------------------------------------------------------------------
# Demo / self-test
# --------------------------------------------------------------------
if __name__ == "__main__":
    def gather(buffer):
        result = ""
        for char in buffer:
            result += char
        return result

    # Basic test: normal strings.
    buf = BetterIterator(["ab", "c"])
    assert gather(buf) == "abc"
    print("✓ ['ab', 'c'] → 'abc'")

    # Empty string in list: should be skipped.
    buf = BetterIterator(["a", ""])
    assert gather(buf) == "a"
    print("✓ ['a', ''] → 'a'")

    # Multiple empty strings.
    buf = BetterIterator(["", "x", "", "y", ""])
    assert gather(buf) == "xy"
    print("✓ ['', 'x', '', 'y', ''] → 'xy'")

    # Nested loops still work.
    buf = BetterIterator(["a", "b"])
    result = ""
    for outer in buf:
        for inner in buf:
            result += inner
    assert result == "abab"
    print("✓ nested loops produce 'abab'")
