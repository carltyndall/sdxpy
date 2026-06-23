"""Solution: Simple Arithmetic exercise.

Write a function that accepts a string consisting of numbers and the basic
arithmetic operations +, -, *, and /, and produces a nested structure
showing the operations in the correct order.  For example, 1 + 2 * 3
should produce ["+", 1, ["*", 2, 3]].
"""


def parse_arithmetic(text):
    """Parse an arithmetic expression into a nested operator tree."""
    tokens = _tokenize(text)
    tree, _ = _expr(tokens)
    return tree


def _tokenize(text):
    """Convert raw string into tokens: numbers and operators."""
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        elif ch in ("+", "-", "*", "/", "(", ")"):
            tokens.append(ch)
            i += 1
        elif ch.isdigit():
            start = i
            while i < len(text) and text[i].isdigit():
                i += 1
            tokens.append(int(text[start:i]))
        else:
            raise ValueError(f"unexpected character '{ch}' at position {i}")
    return tokens


def _expr(tokens):
    """Parse addition/subtraction (lowest precedence)."""
    left, tokens = _term(tokens)
    while tokens and tokens[0] in ("+", "-"):
        op = tokens.pop(0)
        right, tokens = _term(tokens)
        left = [op, left, right]
    return left, tokens


def _term(tokens):
    """Parse multiplication/division (higher precedence)."""
    left, tokens = _factor(tokens)
    while tokens and tokens[0] in ("*", "/"):
        op = tokens.pop(0)
        right, tokens = _factor(tokens)
        left = [op, left, right]
    return left, tokens


def _factor(tokens):
    """Parse a number or a parenthesised sub-expression."""
    if not tokens:
        raise ValueError("unexpected end of input")
    front = tokens.pop(0)
    if isinstance(front, int):
        return front, tokens
    elif front == "(":
        expr, tokens = _expr(tokens)
        if not tokens or tokens[0] != ")":
            raise ValueError("expected ')'")
        tokens.pop(0)               # consume ')'
        return expr, tokens
    else:
        raise ValueError(f"unexpected token {front!r}")


if __name__ == "__main__":
    examples = [
        "1 + 2 * 3",
        "1 * 2 + 3",
        "1 + 2 + 3",
        "1 * 2 * 3",
        "10 / 2 + 3 * 4",
        "(1 + 2) * 3",
        "1 + (2 + 3) * 4",
    ]

    for s in examples:
        result = parse_arithmetic(s)
        print(f"Input:     {s}")
        print(f"Result:    {result}")
        print()
