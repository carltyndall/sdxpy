"""Solution for 'Simplify the Logic' exercise.

The original Check._tag_enter method works but can be hard to follow
because it computes a set difference and then merges into an accumulating
dictionary in one dense expression.

The key insight: for each tag node, we collect the set of actual child
tag names, subtract the allowed children from the manifest, and record
any leftover (disallowed) children as problems.

This rewrite splits the logic into named steps, uses an intermediate
variable for allowed children, and adds a short comment so a reader
can see at a glance what each part does.
"""

import sys
import yaml
from bs4 import BeautifulSoup, Tag
from visitor import Visitor


class Check(Visitor):
    def __init__(self, manifest):
        self.manifest = manifest
        self.problems = {}

    def _tag_enter(self, node):
        # Which child tags actually appear inside this node?
        actual = {child.name for child in node
                  if isinstance(child, Tag)}

        # Which tags does the manifest allow here?
        allowed = self.manifest.get(node.name, set())

        # Anything in 'actual' that is not in 'allowed' is a problem.
        disallowed = actual - allowed

        if disallowed:
            if node.name not in self.problems:
                self.problems[node.name] = set()
            self.problems[node.name] |= disallowed


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
