"""Solution for the "Alternative Matching" exercise.

Modify the code to do greedy matching instead of lazy matching.  In
greedy matching the ``*`` consumes as many characters as possible
before trying the rest of the pattern, giving characters back only
when necessary.
"""


class Match:
    def __init__(self, rest):
        self.rest = rest if rest is not None else Null()

    def match(self, text):
        result = self._match(text, 0)
        if result is None:
            return None
        end, captures = result
        if end == len(text):
            return captures
        return None


class Null(Match):
    def __init__(self):
        self.rest = None

    def _match(self, text, start):
        return (start, [])


class Lit(Match):
    def __init__(self, chars, rest=None, name=None):
        super().__init__(rest)
        self.chars = chars
        self.name = name or f'Lit("{chars}")'

    def _match(self, text, start):
        end = start + len(self.chars)
        if text[start:end] != self.chars:
            return None
        result = self.rest._match(text, end)
        if result is None:
            return None
        rest_end, captures = result
        return (rest_end, [(self.name, self.chars)] + captures)


class Any(Match):
    """Greedy wildcard: consumes as much as possible first.

    Loops from the end of the string backward so that ``*`` gobbles
    everything up front and only gives characters back when the rest
    of the pattern cannot match.
    """

    def __init__(self, rest=None, name=None):
        super().__init__(rest)
        self.name = name or "Any"

    def _match(self, text, start):
        for i in range(len(text), start - 1, -1):
            result = self.rest._match(text, i)
            if result is not None:
                rest_end, captures = result
                if rest_end == len(text):
                    matched = text[start:i]
                    return (rest_end, [(self.name, matched)] + captures)
        return None


class Either(Match):
    def __init__(self, left, right, rest=None):
        super().__init__(rest)
        self.left = left
        self.right = right

    def _match(self, text, start):
        for pat in [self.left, self.right]:
            result = pat._match(text, start)
            if result is not None:
                inner_end, inner_captures = result
                rest_result = self.rest._match(text, inner_end)
                if rest_result is not None:
                    rest_end, rest_captures = rest_result
                    if rest_end == len(text):
                        return (rest_end, inner_captures + rest_captures)
        return None


def demonstrate():
    """Show the difference between lazy and greedy matching."""

    # With greedy matching, ``a*c`` against ``abcabc`` matches the
    # longest possible run: the first ``*`` consumes ``bcab``.
    pat = Lit("a", Any(Lit("c"), name="star"), name="start")
    captures = pat.match("abcabc")
    print("Greedy match of a*c against 'abcabc':")
    if captures:
        for name, text in captures:
            print(f"  {name} -> {text!r}")
    else:
        print("  No match (unexpected)")

    # Contrast: a lazy matcher would have ``*`` consume ``b`` only,
    # matching ``"a" "b" "c"`` and leaving ``"abc"`` unmatched.

    # ``*.txt`` against ``readme.txt`` — greedy captures the whole
    # base name.
    pat = Any(Lit(".txt", name='Lit(".txt")'), name="base")
    captures = pat.match("readme.txt")
    print("\nGreedy match of *.txt against 'readme.txt':")
    if captures:
        for name, text in captures:
            print(f"  {name} -> {text!r}")

    # Edge: ``*`` against empty string.
    captures = Any().match("")
    print("\nGreedy match of * against '':")
    if captures:
        for name, text in captures:
            print(f"  {name} -> {text!r}")

    print("\nDemonstration complete")


if __name__ == "__main__":
    # Basic correctness checks.
    assert Any().match("") is not None
    assert Any().match("abc") is not None

    # a*c matches abc — greedy Any consumes "b".
    captures = Lit("a", Any(Lit("c"), name="mid"), name="first").match("abc")
    assert captures is not None
    assert ("mid", "b") in captures

    # a*b matches ab — greedy Any consumes "".
    captures = Lit("a", Any(Lit("b"), name="mid"), name="first").match("ab")
    assert captures is not None
    assert ("mid", "") in captures

    # a*b matches axb — greedy Any consumes "x".
    captures = Lit("a", Any(Lit("b"), name="mid"), name="first").match("axb")
    assert captures is not None
    assert ("mid", "x") in captures

    # a*b against aaxyb — greedy Any consumes "axy".
    captures = Lit("a", Any(Lit("b"), name="mid"), name="first").match("aaxyb")
    assert captures is not None
    assert ("mid", "axy") in captures

    demonstrate()
