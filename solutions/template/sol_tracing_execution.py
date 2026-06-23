"""Solution: Tracing Execution exercise.

Add a <span z-trace="variable"/> directive that prints the current value
of a variable to stderr for debugging during template expansion.
"""

import sys
from bs4 import BeautifulSoup

from env import Env
from visitor import Visitor
from expander import Expander


def open(expander, node):
    """Print the variable name and its current value to stderr."""
    expander.showTag(node, False)
    name = node.attrs["z-trace"]
    value = expander.env.find(name)
    print(f"z-trace: {name} = {value!r}", file=sys.stderr)
    return True


def close(expander, node):
    expander.showTag(node, True)


def main():
    html = '<html><body><span z-trace="greeting"/> <span z-var="greeting"/></body></html>'
    doc = BeautifulSoup(html, "html.parser")
    expander = Expander(doc.find("html"), {"greeting": "hello"})
    expander.handlers["z-trace"] = sys.modules[__name__]
    expander.walk()
    print("Output:", expander.getResult())


if __name__ == "__main__":
    main()
