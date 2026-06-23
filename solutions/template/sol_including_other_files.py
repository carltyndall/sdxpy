"""Solution: Including Other Files exercise.

Add a directive <div z-include="filename.html"/> that includes another
file in the file being processed, and discuss the two processing orders.
"""

import sys
import os
from bs4 import BeautifulSoup

from expander import Expander


def open(expander, node):
    """Read and expand the named file, inserting the result inline."""
    filename = node.attrs["z-include"]
    if not os.path.exists(filename):
        expander.output(f"<!-- missing include: {filename} -->")
        return False
    with open(filename, "r") as reader:
        included_doc = BeautifulSoup(reader.read(), "html.parser")
    # Push a fresh environment frame so the included file has its own scope.
    expander.env.push({})
    expander.walk(included_doc.find("html"))
    expander.env.pop()
    return False


def close(expander, node):
    pass  # self-closing directive; no closing tag needed.


def main():
    # Write a temporary included file.
    included = "sol_including_other_files_included.html"
    with open(included, "w") as writer:
        writer.write("<html><body><p>from include: <span z-var=\"msg\"/></p></body></html>")

    html = (
        "<html><body>"
        '<div z-include="{}"/>'
        "<span z-var=\"msg\"/>"
        "</body></html>"
    ).format(included)

    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"msg": "outer"})
    expander.handlers["z-include"] = sys.modules[__name__]
    expander.walk()
    print(expander.getResult())

    os.remove(included)


if __name__ == "__main__":
    main()
