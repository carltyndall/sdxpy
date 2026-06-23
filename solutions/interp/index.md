## Solutions

### Arrays

The array exercise asks you to extend the interpreter with fixed-size
one-dimensional lists.  We add three new operations to the lookup table:
`array` creates a Python list filled with `None` values, `aget` reads an
element by index, and `aset` writes an element by index.  Each operation
evaluates its arguments before acting, so you can pass expressions for
the array size or the index rather than just constants.

Storing the array as a plain Python list keeps the solution minimal.
Because Python lists are mutable, `aset` can modify the array in place
without needing any special reference bookkeeping.  The same array value
can be stored in a variable with `set` and retrieved with `get`, just
like any other value in the interpreter.

[%inc sol_arrays.py %]

### Better Error Handling

This exercise replaces raw `assert` statements with a custom exception
hierarchy and a `catch` control-flow construct.  The first step is
defining `TLLException` as a subclass of Python's `Exception` and
writing a `check` helper that raises it with a human-readable message.

The more interesting part is the `catch` operation.  It takes a body
expression and a handler list.  If the body raises a `TLLException`, the
interpreter binds the error message to a variable named in the handler
and then executes the handler's body.  Non-TLL exceptions propagate
unchanged so Python-level bugs are not swallowed silently.  The handler
body is wrapped in an implicit `seq` when it contains more than one
expression, so you can write multi-step recovery logic.

[%inc sol_better_error_handling.py %]

### More Statements

The `print` operation evaluates each of its arguments and displays them
with `print(*values)`.  It returns `None` because its purpose is the
side effect, not a computed value.

The `repeat` operation evaluates a count expression and then executes a
body expression that many times.  The subtle bug in the original
`do_repeat` appeared when the count was zero: `result` was never
assigned, so returning it caused an `UnboundLocalError`.  The fix is
simple --- initialise `result` to `None` before the loop.  When the loop
runs zero times, `result` stays `None` and `do_repeat` returns it
without error.

[%inc sol_more_statements.py %]

### Tracing

The tracing exercise adds a `--trace` flag that makes the interpreter
print each operation call and its result.  We use a module-level `TRACE`
boolean and a small `trace` helper that checks it before printing.  Each
`do_*` function calls `trace` after computing its result, passing the
operation name, the raw argument list, and the computed value.

The command-line parsing is a minimal scan of `sys.argv`.  If the first
argument is `--trace`, we flip the flag and advance past it; the
remaining argument must be the program filename.  This keeps the
solution self-contained without pulling in `argparse`.

[%inc sol_tracing.py %]

### While Loops

The `while` operation evaluates a condition expression and, as long as
it is truthy, evaluates a body expression.  The implementation uses a
Python `while` loop internally, which is the most readable choice.  A
recursive version would work too, but it risks hitting Python's
recursion limit for programs that loop many times.

As with `repeat`, we initialise `result` to `None` so the function has a
well-defined return value when the condition is false on the first
evaluation.

[%inc sol_while_loops.py %]

### Internal Checks

Defensive programming means adding checks that catch impossible-seeming
situations before they cause confusing failures later.  Beyond the
argument-count assertions already in the interpreter, sensible additions
include:

- Checking that arithmetic operands are actually numbers before adding
  or taking absolute values.  If someone writes `["add", "hello", 3]`,
  the error should say "add: left operand is str" rather than producing
  a cryptic `TypeError` from Python's `+`.
- Checking that `get` and `set` receive string variable names.  A
  non-string name means something went wrong in an earlier evaluation
  step, and a clear assertion helps narrow down where.
- Checking that expression lists are never empty (no empty `[]`).
- Checking that stored values are not `None` when the program later
  assumes they are numbers.

Which of these can be type hints instead?  Type hints can express "this
is a list" or "this returns an integer", but they are checked statically
by tools like `mypy` and are not enforced at runtime.  They cannot
replace checks for list length, value ranges, or the presence of a key
in a dictionary.  You can encode *some* constraints with fancy typing
constructs like `Literal` types or `Annotated`, but the complexity grows
quickly and the error messages are less friendly than a plain `assert`
with a descriptive message.  The pragmatic answer is to use type hints
for shape documentation and `assert` for runtime invariants.

[%inc sol_internal_checks.py %]

