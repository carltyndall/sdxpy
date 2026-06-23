"""
Demonstrate why the alias marker ends with a colon.

The persistence framework stores each value as a line with three
colon-separated fields: ``key:ident:value``.  An alias marker has the
key ``"alias"``, the object's ID as its ident, and an empty value
because there is nothing more to store for an alias --- the loader
just needs to know which previously-seen object to return.

If we omitted the trailing colon, the line would be ``alias:12345678``
with only two fields.  The loader splits on ``:`` with ``maxsplit=2``
and expects exactly three fields; a two-field line would cause an
assertion failure.
"""

from io import StringIO


# Simulate what the framework writes for an alias marker.
def show_alias_format():
    thing_id = 12345678
    # This is what SaveAlias._write("alias", thing_id, "") produces:
    line = ":".join(str(f) for f in ("alias", thing_id, ""))
    print(f"alias line: {line!r}")

    fields = line.split(":", maxsplit=2)
    print(f"fields after split: {fields}")
    print(f"number of fields: {len(fields)}")

    # Without the trailing colon:
    broken = ":".join(str(f) for f in ("alias", thing_id))
    print(f"\nbroken line: {broken!r}")
    broken_fields = broken.split(":", maxsplit=2)
    print(f"broken fields: {broken_fields}")
    print(f"number of broken fields: {len(broken_fields)}")


if __name__ == "__main__":
    show_alias_format()
