"""Solution: Counting Loops exercise.

Add a directive <div z-index="indexName" z-limit="limitName">...</div>
that loops from zero to the value in the variable limitName, putting the
current iteration index in indexName.
"""

import sys
from bs4 import BeautifulSoup

from expander import Expander


def open(expander, node):
    """Loop from 0 to limit-1, setting the index variable on each pass."""
    index_name = node.attrs["z-index"]
    limit_name = node.attrs["z-limit"]
    limit = expander.env.find(limit_name)
    if limit is None:
        return False
    expander.showTag(node, False)
    for i in range(int(limit)):
        expander.env.push({index_name: i})
        for child in node.children:
            expander.walk(child)
        expander.env.pop()
    return False


def close(expander, node):
    expander.showTag(node, True)


def main():
    html = (
        "<html><body>"
        '<div z-index="i" z-limit="count">'
        '<p>Item <span z-var="i"/></p>'
        "</div>"
        "</body></html>"
    )
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"count": 3})
    expander.handlers["z-index"] = sys.modules[__name__]
    expander.walk()
    print(expander.getResult())


if __name__ == "__main__":
    main()
