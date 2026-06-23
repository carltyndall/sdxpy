"""Solution for the "Returning Matches" exercise.

Modify the matcher so that it returns the substrings that matched each
part of the expression.  When ``*.txt`` matches ``name.txt`` the
library returns an indication that ``*`` matched ``"name"``.
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
    def __init__(self, rest=None, name=None):
        super().__init__(rest)
        self.name = name or "Any"

    def _match(self, text, start):
        for i in range(start, len(text) + 1):
            result = self.rest._match(text, i)
            if result is not None:
                rest_end, captures = result
                if rest_end == len(text):
                    matched = text[start:i]
                    return (rest_end, [(self.name, matched)] + captures)
        return None


class Either(Match):
    def __init__(self, left, right, rest=None, name=None):
        super().__init__(rest)
        self.left = left
        self.right = right
        self.name = name or "Either"

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


if __name__ == "__main__":
    # Simple literal match.
    captures = Lit("abc").match("abc")
    assert captures == [('Lit("abc")', "abc")], captures

    # Wildcard captures.
    captures = Any().match("hello")
    assert captures == [("Any", "hello")], captures

    # ``*.txt`` matching ``name.txt``.
    pat = Any(Lit(".txt", name='Lit(".txt")'), name="star")
    captures = pat.match("name.txt")
    assert captures is not None
    assert ("star", "name") in captures
    assert ('Lit(".txt")', ".txt") in captures

    # ``a*c`` matching ``abc``.
    pat = Lit("a", Any(Lit("c"), name="middle"), name="start")
    captures = pat.match("abc")
    assert captures is not None, "pattern should match"
    assert ("start", "a") in captures
    assert ("middle", "b") in captures
    assert ('Lit("c")', "c") in captures

    # Non-match returns None.
    assert Lit("abc").match("xyz") is None

    # Empty string to Any.
    captures = Any().match("")
    assert captures == [("Any", "")], captures

    print("All tests passed")
