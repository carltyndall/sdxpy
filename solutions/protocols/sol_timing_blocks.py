"""Solution: a Timer context manager that reports elapsed time."""

import time


class Timer:
    """Context manager that tracks the elapsed time since entering a block.

    The ``elapsed`` method returns the number of seconds (as a float)
    since the ``with`` block was entered.  It can be called any number
    of times while inside the block.
    """

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return False  # never suppress exceptions

    def elapsed(self):
        """Return seconds elapsed since the block was entered."""
        return time.perf_counter() - self._start


# --------------------------------------------------------------------
# Demo / self-test
# --------------------------------------------------------------------
if __name__ == "__main__":
    with Timer() as clock:
        # Simulate a brief operation.
        time.sleep(0.2)
        first = clock.elapsed()
        print(f"after 0.2 s sleep: {first:.3f} seconds")

        time.sleep(0.1)
        second = clock.elapsed()
        print(f"after another 0.1 s: {second:.3f} seconds")

    # Verify that elapsed time grew.
    assert second > first, "elapsed time should increase"
    print("✓ elapsed time increased as expected")

    # Verify that elapsed time is reasonable.
    assert 0.25 < second < 0.50, f"unexpected elapsed time: {second:.3f}"
    print(f"✓ elapsed time {second:.3f}s is in expected range")
