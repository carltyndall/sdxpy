"""Solution: Negation exercise.

Modify the parser so that [!abc] is interpreted as "match anything *except*
one of those three characters."
"""

import string

CHARS = set(string.ascii_letters + string.digits)


class Tokenizer:
    """Tokenizer extended to handle [!...] negation patterns."""

    def __init__(self):
        self._setup()

    def _setup(self):
        self.result = []
        self.current = ""

    def tok(self, text):
        self._setup()
        for ch in text:
            if ch == "*":
                self._add("Any")
            elif ch == "{":
                self._add("EitherStart")
            elif ch == ",":
                self._add(None)
            elif ch == "}":
                self._add("EitherEnd")
            elif ch == "[":
                self._add("CharsetStart")
            elif ch == "]":
                self._add("CharsetEnd")
            elif ch == "!":
                self._add("Not")
            elif ch in CHARS:
                self.current += ch
            else:
                raise NotImplementedError(f"what is '{ch}'?")
        self._add(None)
        return self.result

    def _add(self, thing):
        if len(self.current) > 0:
            self.result.append(["Lit", self.current])
            self.current = ""
        if thing is not None:
            self.result.append([thing])


# --- Match classes with a new Not node ---

class Match:
    def __init__(self, rest):
        self.rest = rest if rest else Null()

    def __eq__(self, other):
        return (other is not None
                and self.__class__ == other.__class__
                and self.rest == other.rest)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class Lit(Match):
    def __init__(self, chars, rest=None):
        super().__init__(rest)
        self.chars = chars

    def __eq__(self, other):
        return super().__eq__(other) and self.chars == other.chars

    def __repr__(self):
        rest = "" if isinstance(self.rest, Null) else f", {self.rest!r}"
        return f"Lit({self.chars!r}{rest})"


class Any(Match):
    def __init__(self, rest=None):
        super().__init__(rest)


class Either(Match):
    def __init__(self, children, rest=None):
        super().__init__(rest)
        self.children = children

    def __eq__(self, other):
        return super().__eq__(other) and self.children == other.children

    def __repr__(self):
        kids = ", ".join(repr(c) for c in self.children)
        rest = "" if isinstance(self.rest, Null) else f", {self.rest!r}"
        return f"Either([{kids}]{rest})"


class Not(Match):
    """Match anything *except* one of the given characters."""

    def __init__(self, excluded, rest=None):
        super().__init__(rest)
        self.excluded = excluded  # set of characters to reject

    def __eq__(self, other):
        return super().__eq__(other) and self.excluded == other.excluded

    def __repr__(self):
        chars = "".join(sorted(self.excluded))
        rest = "" if isinstance(self.rest, Null) else f", {self.rest!r}"
        return f"Not({chars!r}{rest})"


class Null(Match):
    def __init__(self):
        self.rest = None


# --- Parser extended for negation ---

class Parser:
    def parse(self, text):
        tokens = Tokenizer().tok(text)
        return self._parse(tokens)

    def _parse(self, tokens):
        if not tokens:
            return Null()

        front, back = tokens[0], tokens[1:]

        if front[0] == "Any":
            return Any(self._parse(back))
        elif front[0] == "EitherStart":
            return self._parse_EitherStart(front[1:], back)
        elif front[0] == "CharsetStart":
            return self._parse_CharsetStart(front[1:], back)
        elif front[0] == "Lit":
            return Lit(front[1], self._parse(back))
        else:
            assert False, f"Unknown token type {front}"

    def _parse_EitherStart(self, rest, back):
        if (len(back) < 3
                or back[0][0] != "Lit"
                or back[1][0] != "Lit"
                or back[2][0] != "EitherEnd"):
            raise ValueError("badly-formatted Either")
        left = Lit(back[0][1])
        right = Lit(back[1][1])
        return Either([left, right], self._parse(back[3:]))

    def _parse_CharsetStart(self, rest, back):
        """Handle [abc] and [!abc] patterns."""
        if not back:
            raise ValueError("unclosed character set")

        negated = False
        if back[0][0] == "Not":
            negated = True
            back = back[1:]

        children = []
        while back and back[0][0] == "Lit":
            children.append(Lit(back[0][1]))
            back = back[1:]

        if not children:
            raise ValueError("empty character set")

        if not back or back[0][0] != "CharsetEnd":
            raise ValueError("unclosed character set")

        if negated:
            excluded = {c.chars for c in children}
            return Not(excluded, self._parse(back[1:]))
        else:
            return Either(children, self._parse(back[1:]))


if __name__ == "__main__":
    p = Parser()

    # [!abc] should become Not({'a', 'b', 'c'})
    result = p.parse("[!abc]")
    print("Input:    [!abc]")
    print("Result:  ", result)
    # Expected: Not({'a', 'b', 'c'})

    # Plain [abc] still works as Either
    result = p.parse("[abc]")
    print("Input:    [abc]")
    print("Result:  ", result)
    # Expected: Either([Lit('a'), Lit('b'), Lit('c')])

    # Negation combined with Any
    result = p.parse("*[!xyz]")
    print("Input:    *[!xyz]")
    print("Result:  ", result)
    # Expected: Any(Not({'x','y','z'}))
