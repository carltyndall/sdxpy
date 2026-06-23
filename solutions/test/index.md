## Solutions

### Looping Over `globals`

The first snippet raises a `RuntimeError` because of how Python handles
dictionary iteration.  When `for name in globals():` executes, Python
calls `globals()` once to get the module dictionary, then creates an
iterator over its keys.  The loop variable `name` is a new assignment
into the global scope---which means a new key is added to the very
dictionary being iterated over.  Python detects that the dictionary
changed size during iteration and throws its hands up.

The second snippet avoids the problem by creating the `name` variable
before the loop starts.  Now the loop body is merely reassigning an
existing key rather than adding a new one.  The dictionary size stays
the same, the iterator stays valid, and the code prints every global
name including `name` itself.  It is a nice reminder that something as
innocent-looking as a loop variable has subtle mechanics underneath.

[%inc sol_looping_over_globals.py %]

### Individual Results

The original `run_tests` only prints aggregate counts.  We can make it
more informative by recording the name of each test alongside its
outcome.  Instead of a single integer per status we use a list that
collects test names.  After the run we print each test with its result,
then the summary counts just as before.

Testing the test runner itself feels a bit meta, but the pattern is the
same as testing anything else: write functions that deliberately pass,
fail, and error, then check that the runner classifies them correctly.

[%inc sol_individual_results.py %]

### Setup and Teardown

Adding setup and teardown hooks is straightforward once you remember
that functions are just values in a dictionary.  Before running each
test we check whether a function called `setup` exists in `globals()`
and call it if so; after the test we do the same for `teardown`.
Wrapping the teardown call in a `finally` block ensures it runs even
when the test itself blows up, which matters if the teardown is
supposed to close database connections or delete temporary files.

The one subtlety: if `setup` itself raises an exception we probably
should not bother running the test at all, since the fixture is in an
unknown state.  In the implementation below, an exception from `setup`
is caught by the `except Exception` clause, so the test itself never
executes and the outcome is recorded as an error---which is exactly
the right behaviour.

[%inc sol_setup_and_teardown.py %]

### Timing Tests

Python's `time.time()` gives us wall-clock time with sub-second
precision, which is plenty for most tests.  We capture the time before
and after each test call and subtract.  The difference is the elapsed
time in seconds.  For tests that run in microseconds the numbers will
be tiny, so we multiply by 1000 to report milliseconds instead.  The
result tells you which tests are unexpectedly slow---often the first
clue that something is doing more work than it should.

[%inc sol_timing_tests.py %]

### Selecting Tests

Command-line argument parsing does not need to be complicated.  We scan
`sys.argv` for a `-s` or `--select` flag, grab the next item as the
pattern, and filter the test list with Python's `in` operator.  If no
pattern is given we run everything, preserving backward compatibility.
The pattern is a simple substring match against the function name, so
`-s negative` would run only `test_sign_negative` while skipping the
other three.  For more precise control you could switch to `fnmatch` or
a regular expression, but substring matching covers the common cases
well enough.

[%inc sol_selecting_tests.py %]

### Finding Functions

The original runner assumes anything whose name starts with `test_` is
a callable function.  That is a safe assumption when you control the
code, but it costs almost nothing to verify it with Python's built-in
`callable` function.  Adding the check protects you from the day
someone defines `test_data = [1, 2, 3]` at module level and the runner
tries to call a list.

The second part of the exercise asks whether non-callable `test_`
objects should be reported as errors.  There is a case for both
answers.  Reporting them as errors flags accidental name collisions
immediately, which helps beginners who might not understand why their
test isn't running.  Silently skipping them is less noisy and treats
module-level test data as harmless.  The implementation below skips
them quietly, but adding an error report is a one-line change if you
prefer the stricter approach.

[%inc sol_finding_functions.py %]

### Local Variables

Before running the code you can trace through it by hand.  The
`show_locals` function receives two parameters, `low` and `high`, so
those appear in the first `locals()` call.  The `for` loop introduces
`i` as a loop variable, but the key question is *when* `i` becomes
visible.  In Python, the loop variable is assigned at the start of each
iteration---so `i` does not exist before the first iteration, appears
as `1` in the second call to `locals()`, as `2` in the third, and
lingers after the loop finishes because loop variables in Python are
not confined to the loop body.  The variable `i` is still alive with
its final value when `show_locals` prints the last line.  This is why
you can write `for i in range(3): ...; print(i)` and see `2`; it
surprises people coming from languages with block-scoped loop
variables, but it is perfectly consistent with Python's function-level
scoping rules.

[%inc sol_local_variables.py %]

