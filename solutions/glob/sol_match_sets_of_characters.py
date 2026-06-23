"""Solution for the "Match Sets of Characters" exercise.

Add matchers that match any character from a set (``Charset``) and a
convenience matcher for character ranges (``Range``).
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


class Charset(Match):
    """Match a single character if it belongs to a given set."""

    def __init__(self, chars, rest=None):
        super().__init__(rest)
        self.chars = chars

    def _match(self, text, start):
        if start >= len(text):
            return None
        if text[start] not in self.chars:
            return None
        return self.rest._match(text, start + 1)


class Range(Charset):
    """Match a single character in a contiguous range.

    ``Range("a", "z")`` matches any lower-case Latin letter.
    """

    def __init__(self, lo, hi, rest=None):
        chars = "".join(chr(c) for c in range(ord(lo), ord(hi) + 1))
        super().__init__(chars, rest)


if __name__ == "__main__":
    # Charset tests.
    vowel = Charset("aeiou")
    assert vowel.match("a")
    assert vowel.match("e")
    assert vowel.match("i")
    assert vowel.match("o")
    assert vowel.match("u")
    assert not vowel.match("b")
    assert not vowel.match("")
    assert not vowel.match("ab")

    # Charset with rest.
    assert Charset("aeiou", Lit("x")).match("ax")
    assert Charset("aeiou", Lit("x")).match("ex")
    assert not Charset("aeiou", Lit("x")).match("bx")

    # Charset used inside larger pattern.
    assert Lit("a", Charset("xyz", Lit("b"))).match("axb")
    assert Lit("a", Charset("xyz", Lit("b"))).match("ayb")
    assert not Lit("a", Charset("xyz", Lit("b"))).match("awb")

    # Range tests.
    lower = Range("a", "z")
    assert lower.match("a")
    assert lower.match("m")
    assert lower.match("z")
    assert not lower.match("A")
    assert not lower.match("0")
    assert not lower.match("")

    digit = Range("0", "9")
    assert digit.match("0")
    assert digit.match("5")
    assert digit.match("9")
    assert not digit.match("a")
    assert not digit.match("")

    # Range with rest.
    assert Range("a", "z", Lit("1")).match("x1")
    assert not Range("a", "z", Lit("1")).match("X1")

    # Combined use.
    assert Lit("a", Range("0", "9")).match("a3")
    assert not Lit("a", Range("0", "9")).match("ab")

    print("All tests passed")
