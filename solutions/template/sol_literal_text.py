"""Solution: Literal Text exercise.

Add a directive <div z-literal="true">...</div> that copies the enclosed
text as-is without interpreting or expanding any contained directives.
"""

import sys
from bs4 import BeautifulSoup

from expander import Expander


def open(expander, node):
    """Output the opening tag and all raw inner content, then stop recursion."""
    expander.showTag(node, False)
    expander.output(node.decode_contents())
    return False


def close(expander, node):
    expander.showTag(node, True)


def main():
    html = (
        "<html><body>"
        "<div z-literal=\"true\"><span z-var=\"name\"/></div>"
        "<span z-var=\"name\"/>"
        "</body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"name": "Alice"})
    expander.handlers["z-literal"] = sys.modules[__name__]
    expander.walk()
    print(expander.getResult())


if __name__ == "__main__":
    main()
