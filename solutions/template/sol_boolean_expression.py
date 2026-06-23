"""Solution: Boolean Expression exercise.

Design and implement a way to express the Boolean operators `and` and `or`
in the z-if directive.
"""

import sys
from bs4 import BeautifulSoup

from expander import Expander


def open(expander, node):
    """Check a condition that may include 'and' or 'or' operators."""
    condition = node.attrs["z-if"]

    # Try 'or' first (lower precedence).
    if " or " in condition:
        parts = condition.split(" or ")
        result = any(
            expander.env.find(part.strip()) for part in parts
        )
    elif " and " in condition:
        parts = condition.split(" and ")
        result = all(
            expander.env.find(part.strip()) for part in parts
        )
    else:
        result = expander.env.find(condition)

    if result:
        expander.showTag(node, False)
    return bool(result)


def close(expander, node):
    """Close the tag if the condition was true."""
    condition = node.attrs["z-if"]
    if " or " in condition:
        parts = condition.split(" or ")
        result = any(
            expander.env.find(part.strip()) for part in parts
        )
    elif " and " in condition:
        parts = condition.split(" and ")
        result = all(
            expander.env.find(part.strip()) for part in parts
        )
    else:
        result = expander.env.find(condition)
    if result:
        expander.showTag(node, True)


def main():
    html = (
        "<html><body>"
        '<div z-if="a and b"><p>both true</p></div>'
        '<div z-if="a or c"><p>at least one</p></div>'
        '<div z-if="c and d"><p>both false</p></div>'
        "</body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"a": True, "b": True, "c": False, "d": False})
    expander.handlers["z-if"] = sys.modules[__name__]
    expander.walk()
    print(expander.getResult())


if __name__ == "__main__":
    main()
