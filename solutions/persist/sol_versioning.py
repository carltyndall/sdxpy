"""
Demonstrate versioned persistence: write a version marker at the start of
each archive so loaders can detect format changes.

The ``SaveVersioned`` class writes ``version:1`` as the first line before
delegating to ``SaveAlias`` for the actual data.  ``LoadVersioned`` reads
the version line first; if the version is unrecognised it raises an error,
otherwise it continues with ``LoadAlias``.

This is the standard pattern used in libraries like ``pickle`` (which
uses protocol numbers) and in file formats everywhere --- a small header
that tells the reader what rules to follow.
"""

from io import StringIO
from aliasing import SaveAlias, LoadAlias


class SaveVersioned(SaveAlias):
    """Save with a version marker on the first line."""
    VERSION = 1

    def save(self, thing):
        self._write_raw(f"version:{self.VERSION}")
        super().save(thing)

    def _write_raw(self, text):
        print(text, file=self.writer)


class LoadVersioned(LoadAlias):
    """Load a version marker, then delegate to LoadAlias."""
    SUPPORTED = {1}

    def load(self):
        line = self.reader.readline()[:-1]
        assert line.startswith("version:"), \
            f"missing version marker: {line!r}"
        version = int(line.split(":", 1)[1])
        assert version in self.SUPPORTED, \
            f"unsupported archive version {version}"
        return super().load()


def roundtrip(fixture):
    writer = StringIO()
    SaveVersioned(writer).save(fixture)
    data = writer.getvalue()
    print("Saved data:")
    print(data)
    reader = StringIO(data)
    result = LoadVersioned(reader).load()
    return result


if __name__ == "__main__":
    fixture = ["hello", {"a": 1, "b": [2, 3]}]
    result = roundtrip(fixture)
    print(f"Round-tripped: {result}")
    assert result == fixture, f"mismatch: {result} != {fixture}"
    print("Success: versioned round-trip works.")
