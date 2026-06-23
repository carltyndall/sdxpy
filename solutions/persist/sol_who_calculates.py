"""
Demonstrate why ``LoadAlias.load`` must use saved object IDs rather than
calculating fresh ones.

When the saver writes an alias marker like ``alias:4484025600:``, the
number ``4484025600`` is the ``id()`` of the original Python object at
save time.  After saving, that original process may terminate --- the
IDs have no meaning outside the saving session.

The loader must use those IDs as *cross-reference keys* within the
archive.  It stores every object it creates in ``self.seen`` keyed by
the saved ID.  When an alias marker appears later, the loader looks up
that key and returns the already-reconstructed object.  If the loader
calculated fresh IDs with ``id()`` instead, the keys would not match
the ones stored in alias markers and the cross-reference would break.

This script simulates what happens.  Notice that the freshly-loaded
objects have new ``id()`` values different from the saved IDs ---
but the loader's ``seen`` dictionary still works because it keys
everything by the saved (archive) IDs.
"""

from io import StringIO
from aliasing import SaveAlias, LoadAlias


def demonstrate():
    # Create a data structure with aliasing.
    shared = ["shared content"]
    fixture = [shared, shared]

    # Save it and capture the archive text.
    writer = StringIO()
    saver = SaveAlias(writer)
    saver.save(fixture)
    archive = writer.getvalue()

    print("Archive contents:")
    for line in archive.strip().split("\n"):
        print(f"  {line}")
    print()

    # Note the saved IDs from the archive.
    saved_ids = set()
    for line in archive.strip().split("\n"):
        if line.startswith("alias:"):
            continue
        fields = line.split(":", maxsplit=2)
        if len(fields) == 3:
            saved_ids.add(int(fields[1]))
    print(f"Saved IDs in archive: {saved_ids}")

    # Load the data back.
    reader = StringIO(archive)
    loader = LoadAlias(reader)
    result = loader.load()

    # The loaded objects have brand-new Python IDs.
    fresh_ids = {id(result), id(result[0])}
    print(f"Fresh Python IDs after loading: {fresh_ids}")
    print(f"Do saved IDs match fresh IDs? {saved_ids == fresh_ids}")

    # But aliasing is preserved because the loader used
    # the saved IDs as keys in self.seen.
    assert result[0] is result[1], "aliasing broken"
    print("Aliasing preserved even though IDs differ.")


if __name__ == "__main__":
    demonstrate()
