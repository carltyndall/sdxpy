"""Solution: Local Variables.

The show_locals function prints locals() at three points: before the loop,
inside the loop, and after the loop.  The variable 'i' does not exist before
the first iteration; it first appears during loop iteration 1, persists
through iteration 2, and remains alive after the loop finishes because
Python loop variables are function-scoped, not block-scoped.
"""


def show_locals(low, high):
    print(f"start: {locals()}")
    for i in range(low, high):
        print(f"loop {i}: {locals()}")
    print(f"end: {locals()}")


if __name__ == "__main__":
    show_locals(1, 3)
