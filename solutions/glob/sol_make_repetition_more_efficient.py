"""Solution for the "Make Repetition More Efficient" exercise.

Rewrite ``Any`` so that it does not repeatedly re-match text.  The
original implementation tries every split from left to right, which
means the rest of the chain re-examines the same suffixes many times.
This version iterates from right to left so each suffix is tested
exactly once.
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
    """Efficient wildcard: tests suffixes right-to-left.

    By starting from the end of the string and moving leftwards we
    ensure that the rest of the chain examines each suffix exactly
    once.  The original left-to-right loop re-tests suffixes that
    differ by only one character at the front.
    """

    def __init__(self, rest=None):
        super().__init__(rest)

    def _match(self, text, start):
        for i in range(len(text), start - 1, -1):
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
    # Same behaviour as the original Any.
    assert Any().match("")
    assert Any().match("abc")
    assert Any(Lit("def")).match("abcdef")
    assert Lit("abc", Any()).match("abcdef")
    assert Lit("a", Any(Lit("c"))).match("abc")

    # Edge cases.
    assert Lit("a", Any(Lit("b"))).match("ab")
    assert Lit("a", Any(Lit("b"))).match("axxxxxb")
    assert not Lit("a", Any(Lit("b"))).match("ac")

    print("All tests passed")
