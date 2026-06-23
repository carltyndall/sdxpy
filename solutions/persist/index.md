## Solutions

### Dangling Colon

The alias marker line `alias:12345678:` ends with a colon because the
archive format uses three colon-separated fields for every entry:
*key*, *ident*, and *value*.  An alias has no value to store --- all the
loader needs is the key `"alias"` and the identifier of the
already-seen object to return.  The empty third field is still required
so that `line.split(":", maxsplit=2)` produces exactly three fields.
Without the trailing colon, `"alias:12345678"` would split into only
two fields and the loader's assertion would fail with a badly-formed
line error.

The trailing colon is a quirk of using a uniform three-field line
format.  An alternative design could use a two-field format for aliases
and handle it as a special case, but the uniform approach keeps the
parser simpler.

[%inc sol_dangling_colon.py %]

### Versioning

Adding a version marker is straightforward: write `version:1` (or
whatever the current version is) as the very first line of the archive,
and have the loader read and check that line before processing the
rest.  If the version is not one the loader understands, it can raise a
clear error rather than producing garbled data or a cryptic assertion
failure.

The solution below creates `SaveVersioned` and `LoadVersioned` as thin
wrappers around the existing `SaveAlias` and `LoadAlias`.  The saver
emits the version line, then delegates to the parent `save`.  The loader
reads the version line, validates it, and then delegates to the parent
`load`.  In a production system you might dispatch to different loader
implementations based on the version number, allowing old archives to
be read long after the format has evolved.

[%inc sol_versioning.py %]

### Strings

The original framework stores strings by splitting on newlines, writing
the line count, and then writing each physical line on its own.  This
means a single string can occupy an unpredictable number of lines in
the archive.

The alternative is to store the string as a single escaped line.  We
use Python's built-in `repr` to turn the string into a quoted,
escape-sequence form (e.g. `"hello\\nworld"`), and `ast.literal_eval`
to reverse that transformation safely at load time.  Because `repr`
handles quotes, backslashes, tabs, and newlines in one pass, the result
is always exactly one line per string, making the archive easier to
inspect by eye and simpler to process with line-oriented tools.

The solution below subclasses `SaveAlias` and `LoadAlias` and overrides
only the string-handling methods; everything else is inherited.  The
round-trip test includes embedded newlines, double quotes, and
backslashes to verify that the escaping is reversible.

[%inc sol_strings.py %]

### Who Calculates?

`LoadAlias.load` uses the IDs saved in the archive rather than
calculating fresh ones with Python's `id` function because the saved
IDs are the *keys* that tie the archive together.

When `SaveAlias` encounters an object for the second time, it writes an
alias marker containing the object's original `id()`.  Later, when
`LoadAlias` sees that alias marker, it needs to find the
already-reconstructed object that corresponds to that original ID.  It
does this by storing every object it creates in `self.seen` keyed by
the *saved* ID from the archive.  If the loader computed `id()` on the
newly-created objects, those IDs would be different from the ones in
the alias markers (because each Python process assigns its own memory
addresses), and the cross-references would break.

In short: the saved IDs are not about Python-level identity; they are
an internal cross-reference mechanism for the archive format itself.

[%inc sol_who_calculates.py %]

### Using Globals

The first part of this exercise asks you to replace the class-based
dynamic dispatch (`getattr(self, f"save_{typename}")`) with a lookup in
the module's global namespace (`globals()[f"save_{typename}"]`).  This
works: you define `save_int`, `load_int`, etc. as top-level functions
that take the saver or loader instance as their first argument, and the
framework calls them through the `globals()` dictionary.

The second part asks *why this is a bad idea*.  There are several
reasons:

-   It couples the framework to one module's global namespace.  You
    cannot have two loader instances in the same program that handle
    types differently, because they would both look up functions in the
    same dictionary.
-   It makes unit testing awkward.  Each test must ensure the right
    handler functions are present in `globals()` before the framework
    runs; if you forget to register one, you get a confusing
    `ValueError` instead of a clear `AttributeError` pointing at a
    missing method.
-   A function-name typo (e.g. `save_Str` instead of `save_str`)
    becomes a runtime failure rather than something a linter or IDE can
    catch.
-   It breaks encapsulation.  Any code that can write to the module's
    globals can silently change the persistence behaviour of every
    saver and loader in that module.

The class-based dispatch used in the chapter keeps each loader's
handler table private to the instance (via the class hierarchy), which
avoids all of these problems.

[%inc sol_using_globals.py %]
