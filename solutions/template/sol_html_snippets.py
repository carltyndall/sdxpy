"""Solution: HTML Snippets exercise.

Add a directive <div z-snippet="variable">...</div> that saves some text
in a variable so that it can be displayed later via z-var.
"""

import sys
from bs4 import BeautifulSoup

from expander import Expander


def open(expander, node):
    """Capture the inner HTML and store it as a variable."""
    name = node.attrs["z-snippet"]
    raw_content = node.decode_contents()
    # Store in the current topmost environment frame.
    expander.env.stack[-1][name] = raw_content
    return False


def close(expander, node):
    pass  # Snippet definition produces no visible output.


def main():
    html = (
        "<html><body>"
        "<div z-snippet=\"prefix\"><strong>Important:</strong></div>"
        "<p>Expect items</p>"
        "<ul>"
        '<li z-loop="item:names">'
        "<span z-var=\"prefix\"/> <span z-var=\"item\"/>"
        "</li>"
        "</ul>"
        "</body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"names": ["first", "second", "third"]})
    expander.handlers["z-snippet"] = sys.modules[__name__]
    expander.walk()
    print(expander.getResult())


if __name__ == "__main__":
    main()
