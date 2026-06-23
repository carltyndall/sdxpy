"""Solution for 'Detecting Empty Elements' exercise.

We walk the DOM tree looking for Tag nodes that have no children (i.e.,
their `.children` list is empty) but are *not* written as self-closing
tags in the source.  Beautiful Soup's parser normalises `<a></a>` into
a Tag with an empty children list, so we can detect them by checking
`len(node.contents) == 0` together with the `sourceline` attribute for
a nicer report.

We subclass Visitor and override `_tag_enter`: when we see a Tag with
zero children, we record it.  After the visit we print a summary.
"""

import sys
from bs4 import BeautifulSoup, Tag
from visitor import Visitor


class EmptyElementDetector(Visitor):
    def __init__(self):
        self.empty = []

    def _tag_enter(self, node):
        # A Tag with an empty .contents list is written as either
        # <tag/> (self-closing) or <tag></tag> (explicit open/close).
        # Beautiful Soup treats both the same way, so we report all
        # empty elements regardless of source syntax.
        if isinstance(node, Tag) and len(node.contents) == 0:
            line = getattr(node, "sourceline", "?")
            self.empty.append(f"line {line}: <{node.name}>")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        text = reader.read()
    doc = BeautifulSoup(text, "html.parser")

    detector = EmptyElementDetector()
    detector.visit(doc)

    if detector.empty:
        print("Elements that could be self-closing:")
        for entry in detector.empty:
            print(f"  {entry}")
    else:
        print("No empty elements found.")
