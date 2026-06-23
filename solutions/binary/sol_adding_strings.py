"""Solution for 'Adding Strings' exercise.

Add two strings of decimal digits without converting either string to
a number.  We implement grade-school column addition with a carry,
processing the reversed strings so that the rightmost (least
significant) digits align naturally.
"""


def add_str(left, right):
    """Return the decimal sum of *left* and *right* as a string.

    Both arguments must be strings containing only decimal digits.
    The function never calls int() or float() on the inputs.
    """
    # Work from right to left.
    left = left[::-1]
    right = right[::-1]

    carry = 0
    digits = []

    # Extend the shorter string with virtual '0' digits.
    max_len = max(len(left), len(right))
    for i in range(max_len):
        a = ord(left[i]) - ord("0") if i < len(left) else 0
        b = ord(right[i]) - ord("0") if i < len(right) else 0
        total = a + b + carry
        digits.append(chr((total % 10) + ord("0")))
        carry = total // 10

    if carry:
        digits.append(chr(carry + ord("0")))

    # Reverse back to most-significant-first order.
    return "".join(reversed(digits))


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        result = add_str(sys.argv[1], sys.argv[2])
        print(result)
    else:
        # Quick built-in tests.
        assert add_str("12", "5") == "17"
        assert add_str("99", "1") == "100"
        assert add_str("0", "0") == "0"
        assert add_str("123", "456") == "579"
        assert add_str("999", "1") == "1000"
        print("All tests passed.")
