"""Solution for the "Multiple Alternatives" exercise.

Modify ``Either`` so that it can match any number of sub-patterns, not
just two.  When no sub-patterns are specified the matcher fails
immediately.
"""


class Match:
    def __init__(self, rest):
        self.rest = rest if rest is not None else Null()

    def match(self, text):
        result = self._match(text, 0)
        return result == len(text)


class Null(Match):
    def __init__(self):
        self.rest = None

    def _match(self, text, start):
        return start


class Lit(Match):
    def __init__(self, chars, rest=None):
        super().__init__(rest)
        self.chars = chars

    def _match(self, text, start):
        end = start + len(self.chars)
        if text[start:end] != self.chars:
            return None
        return self.rest._match(text, end)


class Any(Match):
    def __init__(self, rest=None):
        super().__init__(rest)

    def _match(self, text, start):
        for i in range(start, len(text) + 1):
            end = self.rest._match(text, i)
            if end == len(text):
                return end
        return None


class Either(Match):
    """Match any one of several sub-patterns.

    ``Either(p1, p2, p3, rest=Null())`` tries ``p1``, then ``p2``,
    then ``p3``, and succeeds if any of them do.
    """

    def __init__(self, *patterns, rest=None):
        super().__init__(rest)
        self.patterns = patterns

    def _match(self, text, start):
        for pat in self.patterns:
            end = pat._match(text, start)
            if end is not None:
                end = self.rest._match(text, end)
                if end == len(text):
                    return end
        return None


if __name__ == "__main__":
    # Two alternatives (old behaviour).
    assert Either(Lit("a"), Lit("b")).match("a")
    assert Either(Lit("a"), Lit("b")).match("b")
    assert not Either(Lit("a"), Lit("b")).match("c")

    # Three alternatives.
    assert Either(Lit("a"), Lit("b"), Lit("c")).match("a")
    assert Either(Lit("a"), Lit("b"), Lit("c")).match("b")
    assert Either(Lit("a"), Lit("b"), Lit("c")).match("c")
    assert not Either(Lit("a"), Lit("b"), Lit("c")).match("d")

    # One alternative.
    assert Either(Lit("x")).match("x")
    assert not Either(Lit("x")).match("y")

    # Zero alternatives: never matches.
    assert not Either().match("")
    assert not Either().match("abc")

    # With rest.
    pat = Either(Lit("a"), Lit("b"), Lit("c"), rest=Lit("x"))
    assert pat.match("ax")
    assert pat.match("bx")
    assert pat.match("cx")
    assert not pat.match("dx")

    print("All tests passed")
