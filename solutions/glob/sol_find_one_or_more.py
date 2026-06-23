"""Solution for the "Find One or More" exercise.

Extend the glob matcher to support ``+``, meaning "match one or more
characters".
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


class OneOrMore(Match):
    """Match one or more characters, like the ``+`` operator."""

    def __init__(self, rest=None):
        super().__init__(rest)

    def _match(self, text, start):
        # Start at start + 1 because we must consume at least one char.
        for i in range(start + 1, len(text) + 1):
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


if __name__ == "__main__":
    # ``+`` requires at least one character.
    assert OneOrMore().match("x")
    assert OneOrMore().match("abc")
    assert not OneOrMore().match("")

    # ``a+b`` matches "ab", "aab", but not "b" or "acb".
    assert Lit("a", OneOrMore(Lit("b"))).match("ab")
    assert Lit("a", OneOrMore(Lit("b"))).match("aab")
    assert Lit("a", OneOrMore(Lit("b"))).match("aaaaab")
    assert not Lit("a", OneOrMore(Lit("b"))).match("b")
    assert not Lit("a", OneOrMore(Lit("b"))).match("acb")

    # Compare with ``*`` which does match zero characters.
    assert Any().match("")
    assert not OneOrMore().match("")

    # ``a+x`` with alternatives.
    pat = Lit("a", OneOrMore(Either(Lit("x"), Lit("y"))))
    assert pat.match("ax")
    assert pat.match("axxxy")
    assert not pat.match("a")

    print("All tests passed")
