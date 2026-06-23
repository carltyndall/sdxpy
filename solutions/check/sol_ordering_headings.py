"""Solution for 'Ordering Headings' exercise.

We check two rules for heading elements (h1 -- h6):

1.  There must be exactly one `<h1>` and it must be the first heading
    encountered in document order.
2.  Heading levels must never skip more than one level: an `<h2>` may
    be followed by `<h3>` but not directly by `<h4>` (or higher).

The implementation collects all heading Tags in traversal order during
`_tag_enter`, then validates the collected list in `_tag_exit` of the
root element so that the analysis runs once at the end.
"""

import sys
from bs4 import BeautifulSoup, Tag
from visitor import Visitor


class HeadingChecker(Visitor):
    def __init__(self):
        self.headings = []
        self.errors = []

    def _tag_enter(self, node):
        if isinstance(node, Tag) and node.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(node)

    def _tag_exit(self, node):
        # Validate once after the full tree has been walked.
        if node.name != "html":
            return

        # Rule 1: exactly one h1, and it must be first.
        levels = [int(h.name[1]) for h in self.headings]
        h1_count = levels.count(1)
        if h1_count == 0:
            self.errors.append("No <h1> element found.")
        elif h1_count > 1:
            self.errors.append(f"Found {h1_count} <h1> elements; expected exactly 1.")
        elif levels[0] != 1:
            self.errors.append("The first heading is not an <h1>.")

        # Rule 2: heading levels must not increase by more than 1.
        for i in range(1, len(levels)):
            if levels[i] > levels[i - 1] + 1:
                prev = self.headings[i - 1]
                cur = self.headings[i]
                line = getattr(cur, "sourceline", "?")
                self.errors.append(
                    f"line {line}: <{cur.name}> directly follows "
                    f"<{prev.name}> (level jump from {levels[i-1]} "
                    f"to {levels[i]})."
                )


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        text = reader.read()
    doc = BeautifulSoup(text, "html.parser")

    checker = HeadingChecker()
    checker.visit(doc)

    if checker.errors:
        print("Heading order problems:")
        for err in checker.errors:
            print(f"  {err}")
    else:
        print("Heading order looks good.")
