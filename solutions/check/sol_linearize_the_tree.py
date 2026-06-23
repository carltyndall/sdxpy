"""Solution for 'Linearize the Tree' exercise.

We want a visitor that produces a flat list of every node (both Tags
and NavigableStrings) in depth-first traversal order --- the same order
`Visitor.visit` follows.  The `ex_flatten.py` snippet in the exercise
shows the desired API:

    for node in Flatten(doc.html).result():
        print(node)

Our `Flatten` class collects each node as `_tag_enter` fires for Tags
and `_text` fires for NavigableStrings.  We expose the collected list
through a `result()` method.
"""

import sys
from bs4 import BeautifulSoup, NavigableString, Tag
from visitor import Visitor


class Flatten(Visitor):
    def __init__(self):
        self._nodes = []

    def _tag_enter(self, node):
        self._nodes.append(node)

    def _text(self, node):
        self._nodes.append(node)

    def result(self):
        return self._nodes


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        text = reader.read()
    doc = BeautifulSoup(text, "html.parser")

    for node in Flatten(doc.html).result():
        if isinstance(node, Tag):
            print(f"TAG <{node.name}>")
        elif isinstance(node, NavigableString):
            content = repr(node.string)
            print(f"TEXT {content}")
