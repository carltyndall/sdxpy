"""
Store strings with escape sequences instead of splitting across multiple
lines.

The original framework stores a string by counting its newlines, writing
that count, and then writing each physical line on its own line.  This
is simple but means a single logical string occupies a variable number
of lines in the archive, which complicates the format.

The alternative shown here uses Python's ``repr`` to produce a single
line with escape sequences like ``\\n``, ``\\t``, and ``\\\\``.  The
loader reverses this with ``ast.literal_eval`` or by decoding the
escapes manually.  The result is one line per string regardless of
content, making the format simpler to inspect and debug.
"""

import ast
from io import StringIO
from aliasing import SaveAlias, LoadAlias


class SaveEscaped(SaveAlias):
    """Save strings as escaped single-line values."""

    def save_str(self, thing):
        escaped = repr(thing)
        self._write("str", id(thing), escaped)


class LoadEscaped(LoadAlias):
    """Load strings by evaluating the escaped representation."""

    def load_str(self, ident, value):
        result = ast.literal_eval(value)
        self.seen[ident] = result
        return result


def roundtrip(fixture):
    writer = StringIO()
    SaveEscaped(writer).save(fixture)
    data = writer.getvalue()
    print("Saved data:")
    print(data)
    reader = StringIO(data)
    result = LoadEscaped(reader).load()
    return result


if __name__ == "__main__":
    # A string with embedded newlines, quotes, and backslashes.
    original = "line one\nline two\nline \"three\" with \\ backslash"
    fixture = [original, {"key": original}]
    result = roundtrip(fixture)
    print(f"Original: {fixture!r}")
    print(f"Result:   {result!r}")
    assert result == fixture, f"mismatch"
    # Also verify aliasing is preserved: the two occurrences should be
    # the same object.
    assert result[0] is result[1]["key"], \
        "aliased string was duplicated"
    print("Success: escaped string round-trip works with aliasing.")
