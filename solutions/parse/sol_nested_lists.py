"""Solution: Nested Lists exercise.

Write a function that accepts a string representing nested lists containing
numbers and returns the actual Python list.  For example, the input
[1, [2, [3, 4], 5]] should produce the corresponding Python list.
"""


def parse_nested_list(text):
    """Parse a string of nested integer lists into Python lists.

    Grammar:
        list   = '[' items ']'
        items  = (number | list) (',' (number | list))*
        number = one or more digits
    """
    tokens = _tokenize(text)
    result, _ = _parse(tokens)
    return result


def _tokenize(text):
    """Convert raw string into tokens: brackets, commas, and integers."""
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        elif ch in ("[", "]", ","):
            tokens.append(ch)
            i += 1
        elif ch.isdigit() or (ch == "-" and i + 1 < len(text) and text[i + 1].isdigit()):
            # Read a (possibly negative) number.
            start = i
            if ch == "-":
                i += 1
            while i < len(text) and text[i].isdigit():
                i += 1
            tokens.append(int(text[start:i]))
        else:
            raise ValueError(f"unexpected character '{ch}' at position {i}")
    return tokens


def _parse(tokens):
    """Recursive descent: read one value from the front of the token list."""
    if not tokens:
        raise ValueError("unexpected end of input")

    front = tokens[0]

    if front == "[":
        # Parse a nested list.
        tokens.pop(0)               # consume '['
        items = []
        if tokens and tokens[0] != "]":
            while True:
                val, tokens = _parse(tokens)
                items.append(val)
                if tokens and tokens[0] == ",":
                    tokens.pop(0)   # consume ','
                else:
                    break
        if not tokens or tokens[0] != "]":
            raise ValueError("expected ']'")
        tokens.pop(0)               # consume ']'
        return items, tokens
    elif isinstance(front, int):
        tokens.pop(0)
        return front, tokens
    else:
        raise ValueError(f"unexpected token {front!r}")


if __name__ == "__main__":
    examples = [
        "[1, 2, 3]",
        "[1, [2, [3, 4], 5]]",
        "[[10, 20], [30, 40]]",
        "[1]",
        "[]",
    ]

    for s in examples:
        result = parse_nested_list(s)
        print(f"Input:     {s}")
        print(f"Result:    {result}")
        print()
