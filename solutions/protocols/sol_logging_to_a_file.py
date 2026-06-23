"""Solution: a decorator that appends a log message to a file on each call."""

import functools
import os
import tempfile


def log_to_file(filename):
    """Return a decorator that logs every call of the wrapped function.

    Each call appends a line to *filename* recording the function name,
    positional arguments, and keyword arguments.  The file is opened in
    append mode for every write so that the log survives even if the
    program crashes partway through.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with open(filename, "a") as log:
                # Build a compact representation of the arguments.
                arg_strs = [repr(a) for a in args]
                arg_strs.extend(f"{k}={v!r}" for k, v in kwargs.items())
                log.write(f"{func.__name__}({', '.join(arg_strs)})\n")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# --------------------------------------------------------------------
# Demo / self-test
# --------------------------------------------------------------------
if __name__ == "__main__":
    # Create a temporary log file so we don't clutter the working tree.
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, suffix=".log", prefix="sdxpy_"
    ) as tmp:
        log_path = tmp.name

    @log_to_file(log_path)
    def add(a, b):
        return a + b

    @log_to_file(log_path)
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    # Call the decorated functions.
    result1 = add(3, 4)
    result2 = greet("Alice")
    result3 = greet("Bob", greeting="Hi")

    # Verify return values are unaffected.
    assert result1 == 7
    assert result2 == "Hello, Alice!"
    assert result3 == "Hi, Bob!"
    print("✓ decorated functions returned correct values")

    # Check the log contents.
    with open(log_path) as f:
        logged = f.read()

    print("log contents:")
    for line in logged.strip().split("\n"):
        print(f"  {line}")

    expected_lines = [
        "add(3, 4)",
        "greet('Alice')",
        "greet('Bob', greeting='Hi')",
    ]
    actual_lines = logged.strip().split("\n")
    assert actual_lines == expected_lines, f"log mismatch: {actual_lines}"
    print("✓ log file contains expected entries")

    # Clean up.
    os.unlink(log_path)
    print("✓ temporary log file removed")
