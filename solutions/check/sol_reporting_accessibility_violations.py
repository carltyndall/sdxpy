"""Solution for 'Reporting Accessibility Violations' exercise.

We build a single visitor that handles all three sub-tasks:

1.  Report every `<img>` that lacks an `alt` attribute.
2.  Report every `<figure>` that does not contain exactly one
    `<figcaption>` child.
3.  Report images inside figures whose `alt` text duplicates the
    figure's `<figcaption>` text.

We do all three in one pass by overriding `_tag_enter` and checking
the relevant conditions whenever we encounter an `<img>` or `<figure>`.
"""

import sys
from bs4 import BeautifulSoup, Tag
from visitor import Visitor


class AccessibilityReporter(Visitor):
    def __init__(self):
        self.missing_alt = []
        self.bad_figure = []
        self.redundant_alt = []

    def _tag_enter(self, node):
        # 1. Images without alt attributes.
        if node.name == "img":
            if not node.has_attr("alt"):
                line = getattr(node, "sourceline", "?")
                self.missing_alt.append(f"line {line}: <img> missing alt")

        # 2. Figures that don't contain exactly one figcaption.
        if node.name == "figure":
            captions = node.find_all("figcaption", recursive=False)
            if len(captions) != 1:
                line = getattr(node, "sourceline", "?")
                self.bad_figure.append(
                    f"line {line}: <figure> has {len(captions)} "
                    f"<figcaption> child(ren), expected 1"
                )

    def _tag_exit(self, node):
        # 3. Redundant alt: img inside figure whose alt == figcaption text.
        # We check on exit so that all children have been visited.
        if node.name == "figure":
            captions = node.find_all("figcaption", recursive=False)
            if len(captions) != 1:
                return
            caption_text = captions[0].get_text(strip=True)
            if not caption_text:
                return
            for img in node.find_all("img"):
                alt_text = img.get("alt", "").strip()
                if alt_text and alt_text == caption_text:
                    line = getattr(img, "sourceline", "?")
                    self.redundant_alt.append(
                        f"line {line}: <img> alt text duplicates "
                        f"<figcaption> ('{alt_text[:40]}')"
                    )


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        text = reader.read()
    doc = BeautifulSoup(text, "html.parser")

    reporter = AccessibilityReporter()
    reporter.visit(doc)

    if reporter.missing_alt:
        print("Images without alt attribute:")
        for entry in reporter.missing_alt:
            print(f"  {entry}")

    if reporter.bad_figure:
        print("\nFigures with wrong number of figcaptions:")
        for entry in reporter.bad_figure:
            print(f"  {entry}")

    if reporter.redundant_alt:
        print("\nImages with redundant alt text:")
        for entry in reporter.redundant_alt:
            print(f"  {entry}")

    if not (reporter.missing_alt or reporter.bad_figure or reporter.redundant_alt):
        print("No accessibility violations found.")
