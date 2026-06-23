"""Solution: Escape Characters exercise.

Modify the tokenizer to handle escape characters, so that \* is interpreted
as a literal '*' character and \\ is interpreted as a literal backslash.
"""

import string

CHARS = set(string.ascii_letters + string.digits)


class Tokenizer:
    """Tokenizer that supports backslash escaping of special characters."""

    def __init__(self):
        self._setup()

    def _setup(self):
        self.result = []
        self.current = ""

    def tok(self, text):
        self._setup()
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == "\\":
                # Escape: read the next character and treat it as a literal.
                if i + 1 < len(text):
                    self.current += text[i + 1]
                    i += 2
                else:
                    raise ValueError("trailing backslash at end of input")
                continue
            elif ch == "*":
                self._add("Any")
            elif ch == "{":
                self._add("EitherStart")
            elif ch == ",":
                self._add(None)
            elif ch == "}":
                self._add("EitherEnd")
            elif ch in CHARS:
                self.current += ch
            else:
                raise NotImplementedError(f"what is '{ch}'?")
            i += 1
        self._add(None)
        return self.result

    def _add(self, thing):
        if len(self.current) > 0:
            self.result.append(["Lit", self.current])
            self.current = ""
        if thing is not None:
            self.result.append([thing])


if __name__ == "__main__":
    # The escaped star becomes part of the literal, not an Any token.
    tok = Tokenizer()
    print("Input:    hello\\*world")
    print("Tokens:  ", tok.tok("hello\\*world"))
    # Expected: [['Lit', 'hello*world']]

    # Escaped backslash becomes a single literal backslash.
    print("Input:    path\\\\to\\\\file")
    print("Tokens:  ", tok.tok("path\\\\to\\\\file"))
    # Expected: [['Lit', 'path\\to\\file']]

    # Mixed: escaped star and real star.
    print("Input:    a\\*b*c")
    print("Tokens:  ", tok.tok("a\\*b*c"))
    # Expected: [['Lit', 'a*b'], ['Any'], ['Lit', 'c']]
