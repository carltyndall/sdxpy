"""Explain why one counter closure fails and the other succeeds."""


def make_counter_fail():
    """This version raises UnboundLocalError when called."""
    value = 0

    def _inner():
        value += 1  # Assignment creates a local 'value', unbound on first read.
        return value

    return _inner


def make_counter_succeed():
    """This version works because it mutates a list instead of reassigning."""
    value = [0]

    def _inner():
        value[0] += 1  # Mutation, not assignment to 'value' itself.
        return value[0]

    return _inner


def make_counter_nonlocal():
    """This version works by declaring value as nonlocal."""
    value = 0

    def _inner():
        nonlocal value
        value += 1
        return value

    return _inner


# The failing version.
print("make_counter_fail():")
c = make_counter_fail()
try:
    for i in range(3):
        print(c())
except UnboundLocalError as e:
    print(f"  UnboundLocalError: {e}")
    print("  Python sees 'value += 1' as an assignment, making value local.")

# The succeeding version (list mutation).
print("\nmake_counter_succeed():")
c = make_counter_succeed()
for i in range(3):
    print(f"  {c()}")

# The nonlocal fix.
print("\nmake_counter_nonlocal():")
c = make_counter_nonlocal()
for i in range(3):
    print(f"  {c()}")
