"""Solution for 'Performance' exercise.

Measure how much slower element-by-element access is for
``array.array`` compared to a plain Python list.  The array stores raw
C values without per-element object headers, but extracting a value
requires boxing it into a Python ``int`` (or ``float``) on the fly.
"""

import array
import time


SIZE = 1_000_000
REPEATS = 5


def time_accumulate(container, repeats=REPEATS):
    """Time summing all elements of *container*, best of *repeats*."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        total = 0
        for v in container:
            total += v
        elapsed = time.perf_counter() - start
        if elapsed < best:
            best = elapsed
    return best


if __name__ == "__main__":
    values = list(range(SIZE))
    arr = array.array("l", values)

    list_time = time_accumulate(values)
    arr_time = time_accumulate(arr)

    ratio = arr_time / list_time
    print(f"List access:  {list_time:.4f} s")
    print(f"Array access: {arr_time:.4f} s")
    print(f"Slowdown:     {ratio:.2f}x")
