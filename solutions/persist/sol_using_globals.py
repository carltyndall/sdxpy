"""
Demonstrate using ``globals()`` to look up save/load functions instead of
relying on class methods, and explain why this is a bad idea.

Part 1: The ``SaveGlobal`` class searches the global namespace for a
function named ``save_<typename>`` (e.g. ``save_int``) and calls it
directly, passing ``self`` as the first argument.  ``LoadGlobal`` does
the same for ``load_<typename>`` functions.  This lets you register new
type handlers by defining module-level functions --- no subclassing
required.

Part 2: This approach is fragile for several reasons.  First, it
couples the framework to the module's global namespace, so you cannot
have two loaders with different handler sets in the same program.
Second, it makes testing harder because you must pollute or mock the
module's namespace.  Third, a typo in a function name becomes a
runtime error ("function not found") instead of a clear
``AttributeError``.  Finally, it breaks encapsulation: any code that
can write to the module's globals can change the persistence behaviour
of every saver and loader in that module.
"""

from io import StringIO


# --- Framework using globals() ---

class SaveGlobal:
    """Save objects by dispatching to ``save_<type>`` functions in globals."""

    def __init__(self, writer):
        self.writer = writer
        self.seen = set()

    def _write(self, *fields):
        print(":".join(str(f) for f in fields), file=self.writer)

    def save(self, thing):
        thing_id = id(thing)
        if thing_id in self.seen:
            self._write("alias", thing_id, "")
            return
        self.seen.add(thing_id)
        typename = type(thing).__name__
        func_name = f"save_{typename}"
        func = globals().get(func_name)
        if func is None:
            raise ValueError(f"unknown type {typename}")
        func(self, thing)


class LoadGlobal:
    """Load objects by dispatching to ``load_<type>`` functions in globals."""

    def __init__(self, reader):
        self.reader = reader
        self.seen = {}

    def load(self):
        line = self.reader.readline()[:-1]
        assert line, "Nothing to read"
        fields = line.split(":", maxsplit=2)
        assert len(fields) == 3, f"Badly-formed line {line}"
        key, ident, value = fields

        if key == "alias":
            return self.seen[ident]

        func_name = f"load_{key}"
        func = globals().get(func_name)
        if func is None:
            raise ValueError(f"unknown type {key}")
        result = func(self, ident, value)
        self.seen[ident] = result
        return result


# --- Type-specific handlers at module level ---

def save_int(saver, thing):
    saver._write("int", id(thing), thing)


def load_int(loader, ident, value):
    result = int(value)
    loader.seen[ident] = result
    return result


def save_str(saver, thing):
    lines = thing.split("\n")
    saver._write("str", id(thing), len(lines))
    for line in lines:
        print(line, file=saver.writer)


def load_str(loader, ident, value):
    result = "\n".join(
        [loader.reader.readline()[:-1] for _ in range(int(value))]
    )
    loader.seen[ident] = result
    return result


def save_list(saver, thing):
    saver._write("list", id(thing), len(thing))
    for item in thing:
        saver.save(item)


def load_list(loader, ident, length):
    result = []
    loader.seen[ident] = result
    for _ in range(int(length)):
        result.append(loader.load())
    return result


def save_dict(saver, thing):
    saver._write("dict", id(thing), len(thing))
    for k, v in thing.items():
        saver.save(k)
        saver.save(v)


def load_dict(loader, ident, length):
    result = {}
    loader.seen[ident] = result
    for _ in range(int(length)):
        k = loader.load()
        v = loader.load()
        result[k] = v
    return result


# --- Demonstrate round-trip ---

def roundtrip(fixture):
    writer = StringIO()
    SaveGlobal(writer).save(fixture)
    data = writer.getvalue()
    print("Saved data:")
    print(data)
    reader = StringIO(data)
    result = LoadGlobal(reader).load()
    return result


if __name__ == "__main__":
    fixture = [1, "hello", {"key": [2, 3]}]
    result = roundtrip(fixture)
    print(f"Result: {result}")
    assert result == fixture, f"mismatch: {result!r} != {fixture!r}"
    print("Success: globals-based round-trip works.")
    print()
    print("Why this is a bad idea:")
    print("- Handler functions live in module scope, not on a class.")
    print("- You cannot have two loaders with different handler sets.")
    print("- Testing requires messing with the module namespace.")
    print("- A typo in a function name is a runtime error.")
    print("- Any code can alter persistence behaviour by editing globals.")
