"""Solution for the "Filtering by Strings" exercise.

Modify the filter/select comparison to use string columns instead of
integers.  Create random 4-letter strings and benchmark exact-match,
prefix, and substring filtering.
"""

import random
import string
import time
from df_col import DfCol
from df_row import DfRow

LETTERS = string.ascii_uppercase


def random_string(length=4):
    return "".join(random.choice(LETTERS) for _ in range(length))


def make_row(nrow, ncol):
    labels = [f"label_{c}" for c in range(ncol)]
    rows = [
        {c: random_string() for c in labels}
        for _ in range(nrow)
    ]
    return DfRow(rows)


def make_col(nrow, ncol):
    cols = {}
    for c in range(ncol):
        cols[f"label_{c}"] = [random_string() for _ in range(nrow)]
    return DfCol(**cols)


def benchmark(label, df, filter_func):
    t0 = time.time()
    df.filter(filter_func)
    return time.time() - t0


if __name__ == "__main__":
    nrow, ncol = 500, 20
    df_row = make_row(nrow, ncol)
    df_col = make_col(nrow, ncol)

    # Grab a value from the first column to use as a filter target.
    target = df_row.get("label_0", 0)

    # --- exact match ---
    def exact_match(label_0, **kwargs):
        return label_0 == target

    tr_exact = benchmark("exact (row)", df_row, exact_match)
    tc_exact = benchmark("exact (col)", df_col, exact_match)

    # --- starts with ---
    prefix_char = target[0]

    def starts_with(label_0, **kwargs):
        return label_0.startswith(prefix_char)

    tr_prefix = benchmark("prefix (row)", df_row, starts_with)
    tc_prefix = benchmark("prefix (col)", df_col, starts_with)

    # --- contains ---
    inner_char = target[1]

    def contains(label_0, **kwargs):
        return inner_char in label_0

    tr_contains = benchmark("contains (row)", df_row, contains)
    tc_contains = benchmark("contains (col)", df_col, contains)

    print(f"Data size: {nrow} rows x {ncol} cols\n")
    print(f"{'Operation':<20} {'DfRow (s)':>12} {'DfCol (s)':>12}")
    print("-" * 46)
    print(f"{'exact match':<20} {tr_exact:>12.6f} {tc_exact:>12.6f}")
    print(f"{'starts with':<20} {tr_prefix:>12.6f} {tc_prefix:>12.6f}")
    print(f"{'contains':<20} {tr_contains:>12.6f} {tc_contains:>12.6f}")

    print()
    print(
        "With string columns, the relative performance gap between "
        "row-wise and column-wise storage narrows for filter operations "
        "because string comparisons are slower than integer arithmetic, "
        "diluting the overhead of building the temporary dictionary in "
        "DfCol.filter.  Containment checks (in) are more expensive than "
        "exact equality or startswith, which further reduces the "
        "proportional difference between the two layouts."
    )
