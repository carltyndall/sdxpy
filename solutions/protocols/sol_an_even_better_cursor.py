"""Solution: BetterCursor with _row=0, _col=-1 and _advance first."""


class BetterIterator:
    """Store text lines and produce a fresh cursor for each loop."""

    def __init__(self, text):
        self._text = text[:]

    def __iter__(self):
        return BetterCursor(self._text)


class BetterCursor:
    """Cursor that always calls _advance as the first action in __next__.

    By starting ``_col`` at -1, the very first call to ``_advance``
    moves it to index 0 of the first row.  This means we never have to
    check whether the cursor is "before the first character" in
    ``__next__``---``_advance`` handles that uniformly.
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
        """Advance to the next character, skipping empty rows."""
        while self._row < len(self._text):
            self._col += 1
            if self._col < len(self._text[self._row]):
                return
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

    # Basic iteration.
    buf = BetterIterator(["ab", "c"])
    assert gather(buf) == "abc"
    print("✓ ['ab', 'c'] → 'abc'")

    # Empty strings are skipped.
    buf = BetterIterator(["a", ""])
    assert gather(buf) == "a"
    print("✓ ['a', ''] → 'a'")

    # Nested loops produce independent results.
    buf = BetterIterator(["a", "b"])
    result = ""
    for outer in buf:
        for inner in buf:
            result += inner
    assert result == "abab"
    print("✓ nested loops produce 'abab'")

    # Single-character rows.
    buf = BetterIterator(["x", "y", "z"])
    assert gather(buf) == "xyz"
    print("✓ ['x', 'y', 'z'] → 'xyz'")
