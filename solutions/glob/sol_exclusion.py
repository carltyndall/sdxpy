"""Solution for the "Exclusion" exercise.

Create a ``Not`` matcher that succeeds only when the wrapped pattern
fails to match.
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
    def __init__(self, left, right, rest=None):
        super().__init__(rest)
        self.left = left
        self.right = right

    def _match(self, text, start):
        for pat in [self.left, self.right]:
            end = pat._match(text, start)
            if end is not None:
                end = self.rest._match(text, end)
                if end == len(text):
                    return end
        return None


class Not(Match):
    """Match only when the wrapped pattern does *not* match.

    ``Not(Lit("abc"))`` succeeds for any string that is not exactly
    ``"abc"`` (assuming ``rest`` is ``Null``).
    """

    def __init__(self, pattern, rest=None):
        super().__init__(rest)
        self.pattern = pattern

    def _match(self, text, start):
        # Check every possible match length for the inner pattern.
        for i in range(start, len(text) + 1):
            end = self.pattern._match(text, start)
            if end is not None:
                # The inner pattern matched at this position.  Now check
                # whether the rest of the chain can complete the match.
                rest_end = self.rest._match(text, i)
                if rest_end == len(text):
                    # Inner pattern led to a full match, so Not fails.
                    return None
        # The inner pattern never led to a full match, so Not succeeds.
        return self.rest._match(text, start)


if __name__ == "__main__":
    # ``Not(Lit("abc"))`` succeeds for strings that are not "abc".
    assert Not(Lit("abc")).match("xyz")
    assert Not(Lit("abc")).match("ab")
    assert Not(Lit("abc")).match("abcd")
    assert not Not(Lit("abc")).match("abc")

    # ``Not`` with rest: ``Not(Lit("abc"), Lit("x"))`` matches any
    # single character followed by "x", as long as that character is
    # not "a" followed by "bcx" completing the match.
    assert Not(Lit("abc"), Lit("x")).match("xx")

    # ``Not(Lit("x"))`` in a chain: match "a" then something that is
    # not "x", then "b".
    pat = Lit("a", Not(Lit("x"), Lit("b")))
    assert pat.match("ab")     # a + (not x) + b  —  empty not-x works
    assert pat.match("ayb")    # a + y + b
    assert not pat.match("axb")  # a + x + b  —  fails because x matches

    # ``Not`` with Any: match a string that does not start with "abc".
    pat = Not(Lit("abc"), Any())
    assert pat.match("xyz")
    assert not pat.match("abc")

    print("All tests passed")
