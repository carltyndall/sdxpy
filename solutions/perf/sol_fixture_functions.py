"""Solution for the "Fixture Functions" exercise.

Rewrite the row-wise dataframe tests using pytest's @fixture decorator
instead of plain helper functions.  Fixtures are injected by name into
test functions, which makes them more explicit and lets pytest handle
teardown and sharing.
"""

import pytest
from df_row import DfRow


@pytest.fixture
def odd_even():
    """A small two-row dataframe used by several tests."""
    return DfRow([{"a": 1, "b": 3}, {"a": 2, "b": 4}])


@pytest.fixture
def a_only():
    """A single-column dataframe."""
    return DfRow([{"a": 1}, {"a": 2}])


def test_construct_with_single_value():
    df = DfRow([{"a": 1}])
    assert df.get("a", 0) == 1


def test_construct_with_two_pairs(odd_even):
    assert odd_even.get("a", 0) == 1
    assert odd_even.get("a", 1) == 2
    assert odd_even.get("b", 0) == 3
    assert odd_even.get("b", 1) == 4


def test_nrow(odd_even):
    assert odd_even.nrow() == 2


def test_ncol(odd_even):
    assert odd_even.ncol() == 2


def test_equality(odd_even):
    left = odd_even
    right = DfRow([{"a": 1, "b": 3}, {"a": 2, "b": 4}])
    assert left.eq(right) and right.eq(left)


def test_inequality(odd_even, a_only):
    assert not odd_even.eq(a_only)
    repeated = DfRow([{"a": 1, "b": 3}, {"a": 1, "b": 3}])
    assert not odd_even.eq(repeated)


def test_select(odd_even, a_only):
    selected = odd_even.select("a")
    assert selected.eq(a_only)


def test_filter(odd_even):
    def odd(a, b):
        return (a % 2) == 1

    assert odd_even.filter(odd).eq(DfRow([{"a": 1, "b": 3}]))


# ---------------------------------------------------------------------------
# Run with:  pytest perf/sol_fixture_functions.py -v
# ---------------------------------------------------------------------------
