"""Solution for 'Converting Integers to Bits' exercise.

Two functions implemented using only bitwise operators and character
comparisons (no calls to ``int()``, ``bin()``, or ``format()``):

- ``to_bits`` returns the binary representation of a non-negative
  integer as a string of ``'1'`` and ``'0'`` characters.
- ``from_bits`` converts such a string back into an integer.
"""


def to_bits(n):
    """Return the binary representation of a non-negative integer *n*."""
    if n == 0:
        return "0"
    bits = []
    while n:
        bits.append("1" if (n & 1) else "0")
        n >>= 1
    return "".join(reversed(bits))


def from_bits(s):
    """Convert a string of '1' and '0' into an unsigned integer."""
    result = 0
    for ch in s:
        result <<= 1
        if ch == "1":
            result |= 1
    return result


if __name__ == "__main__":
    # Round-trip sanity checks.
    for value in [0, 1, 2, 7, 8, 13, 31, 42, 127, 255, 1024]:
        bits = to_bits(value)
        recovered = from_bits(bits)
        assert recovered == value, f"mismatch: {value} -> {bits} -> {recovered}"

    # Compare against Python's built-ins.
    for value in range(256):
        assert to_bits(value) == bin(value)[2:], f"to_bits({value}) disagrees"

    print("All tests passed.")
