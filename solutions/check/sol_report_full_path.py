"""Solution for 'Report Full Path' exercise.

The original checker only reports the *parent* tag name when it finds a
disallowed child.  We want it to report the full ancestor path instead,
e.g. `div.div.p` instead of just `p`.

We extend the Check visitor to maintain a stack of ancestor tag names.
When `_tag_enter` fires we push the current tag name, compute problems
using the full path as the key, and pop the tag name in `_tag_exit`.
"""

import sys
import yaml
from bs4 import BeautifulSoup, Tag
from visitor import Visitor


class Check(Visitor):
    def __init__(self, manifest):
        self.manifest = manifest
        self.problems = {}
        self._path = []

    def _tag_enter(self, node):
        self._path.append(node.name)
        actual = {child.name for child in node
                  if isinstance(child, Tag)}
        allowed = self.manifest.get(node.name, set())
        disallowed = actual - allowed

        if disallowed:
            full = ".".join(self._path)
            if full not in self.problems:
                self.problems[full] = set()
            self.problems[full] |= disallowed

    def _tag_exit(self, node):
        self._path.pop()


def read_manifest(filename):
    with open(filename, "r") as reader:
        result = yaml.load(reader, Loader=yaml.FullLoader)
        for key in result:
            result[key] = set(result[key])
        return result


if __name__ == "__main__":
    manifest = read_manifest(sys.argv[1])
    with open(sys.argv[2], "r") as reader:
        text = reader.read()
    doc = BeautifulSoup(text, "html.parser")

    checker = Check(manifest)
    checker.visit(doc.html)
    for key, value in checker.problems.items():
        print(f"{key}: {', '.join(sorted(value))}")
