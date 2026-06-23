"""Solution for 'Eliminating Newlines' exercise.

We want to remove text nodes whose content consists *only* of newline
characters.  The existing Visitor class calls `_text` for every
NavigableString it encounters, so we can detect such nodes without
changing Visitor at all --- we simply override `_text`.

The subtlety is *deletion*.  If we call `node.extract()` during the
walk we risk mutating the tree while the caller (`Visitor.visit`) is
iterating over `.children`.  The safe approach is to collect the
offending nodes during the visit and remove them afterwards.

This script demonstrates both steps: first a collecting visitor, then
a post-processing deletion pass.  After removal it pretty-prints the
cleaned document to show the result.
"""

import sys
from bs4 import BeautifulSoup, NavigableString
from visitor import Visitor


class NewlineCollector(Visitor):
    """Collect NavigableString nodes that contain only whitespace
    (including the common single-newline text nodes)."""

    def __init__(self):
        self.to_remove = []

    def _text(self, node):
        if isinstance(node, NavigableString) and node.string.strip() == "":
            self.to_remove.append(node)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        text = reader.read()
    doc = BeautifulSoup(text, "html.parser")

    collector = NewlineCollector()
    collector.visit(doc)

    for node in collector.to_remove:
        node.extract()

    print(doc.prettify())
