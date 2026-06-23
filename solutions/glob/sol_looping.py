"""Solution for the "Looping" exercise.

Rewrite the matchers so that a top-level object manages a list of
matchers, none of which know about any of the others.
"""


class Match:
    """Top-level matcher that manages a list of sub-matchers.

    Iterates through matchers in order.  A matcher returns either a
    single next position or a list of possible next positions.  When a
    list is returned the coordinator tries each position in order and
    backtracks if the remaining matchers cannot complete the match.
    """

    def __init__(self, matchers):
        self.matchers = matchers

    def match(self, text):
        return self._try_from(text, 0, 0)

    def _try_from(self, text, pos, matcher_index):
        if matcher_index >= len(self.matchers):
            return pos == len(text)
        m = self.matchers[matcher_index]
        result = m.match_at(text, pos)
        if result is None:
            return False
        if isinstance(result, list):
            for next_pos in result:
                if self._try_from(text, next_pos, matcher_index + 1):
                    return True
            return False
        return self._try_from(text, result, matcher_index + 1)


class Lit:
    """Match a literal string."""

    def __init__(self, chars):
        self.chars = chars

    def match_at(self, text, start):
        end = start + len(self.chars)
        if text[start:end] == self.chars:
            return end
        return None


class Any:
    """Match zero or more characters (wildcard).

    Returns a list of all possible next positions so the coordinator
    can try each one in turn.
    """

    def match_at(self, text, start):
        return list(range(start, len(text) + 1))


class Either:
    """Match one of two alternatives."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def match_at(self, text, start):
        for pat in [self.left, self.right]:
            end = pat.match_at(text, start)
            if end is not None:
                return end
        return None


if __name__ == "__main__":
    # fmt: off
    assert Match([Lit("a"), Lit("b")]).match("ab")
    assert not Match([Lit("a"), Lit("b")]).match("abc")
    assert not Match([Lit("a"), Lit("b")]).match("ac")
    assert Match([Lit("a"), Any(), Lit("c")]).match("abc")
    assert Match([Lit("a"), Any(), Lit("c")]).match("axxxc")
    assert Match([Either(Lit("x"), Lit("y"))]).match("x")
    assert Match([Either(Lit("x"), Lit("y"))]).match("y")
    assert not Match([Either(Lit("x"), Lit("y"))]).match("z")
    print("All tests passed")
