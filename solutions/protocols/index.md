## Solutions

### Testing Exceptions

A context manager that checks for an expected exception needs three
pieces: a constructor that remembers the exception type, an `__enter__`
method that does nothing special, and an `__exit__` method that inspects
whatever exception (if any) was raised inside the block.

The logic in `__exit__` has three branches.  If `exc_type` is `None`,
no exception was raised, so we raise an `AssertionError` to fail the
test.  If `exc_type` matches (or is a subclass of) the expected type, we
return `True` to tell Python to suppress the exception---the test
passes.  Otherwise we return `False` to let the unexpected exception
propagate and fail the test in the usual way.

Using `issubclass` rather than an exact identity check makes the context
manager behave like `pytest.raises`: catching `LookupError` also catches
`KeyError` and `IndexError`, which is almost always what you want in a
test.

[%inc sol_testing_exceptions.py %]

### Timing Blocks

The `Timer` class is one of the simplest context managers you can write.
`__enter__` records the current time using `time.perf_counter` (which is
monotonic and unaffected by system clock adjustments) and returns
`self`.  `__exit__` just returns `False` so that any exception in the
block propagates normally.

The `elapsed` method subtracts the stored start time from the current
time each time it is called.  Because `__enter__` returns the `Timer`
instance itself, the variable named in the `with` statement holds a
reference to that instance, and we can call `elapsed` on it as often as
we like.  This lets us check progress at multiple points inside a long
block without creating extra variables.

[%inc sol_timing_blocks.py %]

### Handling Empty Strings

The original `NaiveIterator` crashes with an `IndexError` when it
encounters an empty string because its `_advance` method increments the
column to 0 and immediately discovers that the empty row has length 0,
so it moves to the next row and sets the column to 0 again.  The next
call to `__next__` then tries to index into a row that may not exist.

The fix replaces the simple `if` in `_advance` with a `while` loop that
keeps moving forward as long as it lands on an empty row.  The column
stays at -1 after advancing past an empty row, so the next call to
`_advance` will increment it to 0 and check again.  When we finally land
on a non-empty row, the loop exits and `__next__` can safely return the
character at the current position.

This version also handles the edge case where every row is empty: the
`while` loop runs until `_row` equals `len(self._text)`, at which point
`__next__` raises `StopIteration`.

[%inc sol_handling_empty_strings.py %]

### An Even Better Cursor

The chapter's `BetterCursor` already initializes `_row` to 0 and `_col`
to -1 and calls `_advance` as the first action in `__next__`, so at
first glance this exercise looks like a trick question.  The point is to
appreciate *why* this design is simpler than the naive approach.

Starting `_col` at -1 is a sentinel that means "before the first
character."  Every call to `__next__` unconditionally calls `_advance`,
which increments `_col` to 0 on the very first call.  There is no need
for a special-case check to determine whether we are at the beginning of
iteration: the sentinel absorbs that case into the normal flow.  The
"few other changes" mentioned in the exercise amount to making
`_advance` robust enough to skip empty rows (a `while` loop instead of
an `if`) so that the sentinel works correctly in all cases.

Is this implementation simpler?  It has fewer special cases, which is a
kind of simplicity.  The cost is that `_advance` must handle the "no
valid character remains" situation gracefully, which the `while` loop
does by exhausting the rows.  On balance, the uniform treatment of the
first and subsequent calls to `__next__` makes the code easier to reason
about.

[%inc sol_an_even_better_cursor.py %]

### Logging to a File

The decorator `log_to_file` takes a filename and returns a decorator
that wraps a function.  The wrapper opens the file in append mode on
every call, writes a line recording the function name and arguments, and
then calls the original function.  Opening and closing the file on every
write is deliberately conservative: if the program crashes, all log
entries written so far are safely on disk.  The alternative---keeping
the file open for the lifetime of the program---would be faster but
would lose the last few entries on a crash.

The argument formatting builds a string that looks like a valid Python
call.  Positional arguments are shown with `repr`, and keyword arguments
are formatted as `name=value` pairs.  This makes the log readable while
still being precise about the types of the arguments.

Using `functools.wraps` copies the original function's name and
docstring onto the wrapper, which keeps debugging and introspection
working the way users expect.

[%inc sol_logging_to_a_file.py %]

