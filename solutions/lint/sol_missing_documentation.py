"""Report modules, classes, and functions that lack docstrings."""

import ast
import sys


class MissingDocstrings(ast.NodeVisitor):
    """Find definitions that don't have a docstring."""

    def visit_Module(self, node):
        self._check(node, "module")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self._check(node, f"class {node.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self._check(node, f"function {node.name}")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._check(node, f"async function {node.name}")
        self.generic_visit(node)

    def _check(self, node, label):
        if ast.get_docstring(node) is None:
            print(f"{label} at line {node.lineno} is missing a docstring")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    tree = ast.parse(source)
    checker = MissingDocstrings()
    checker.visit(tree)
