"""Report unused variables including function parameters."""

import ast
import sys
from collections import namedtuple

Scope = namedtuple("Scope", ["name", "load", "store"])


class FindUnusedParameters(ast.NodeVisitor):
    """Find unused variables and unused function parameters."""

    def __init__(self):
        super().__init__()
        self.stack = []

    def visit_Module(self, node):
        self._search("global", node)

    def visit_FunctionDef(self, node):
        # Push a new scope for this function.
        self.stack.append(Scope(node.name, set(), set()))
        # Add each parameter name to the "store" set so it is
        # treated as a definition within this scope.
        for arg in node.args.args:
            self.stack[-1].store.add(arg.arg)
        if node.args.vararg:
            self.stack[-1].store.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.stack[-1].store.add(node.args.kwarg.arg)
        # Recurse through the function body.
        self.generic_visit(node)
        scope = self.stack.pop()
        self._check(scope)

    def _search(self, name, node):
        self.stack.append(Scope(name, set(), set()))
        self.generic_visit(node)
        scope = self.stack.pop()
        self._check(scope)

    def _check(self, scope):
        unused = scope.store - scope.load
        if unused:
            names = ", ".join(sorted(unused))
            print(f"unused in {scope.name}: {names}")

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.stack[-1].load.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.stack[-1].store.add(node.id)
        else:
            assert False, "Unknown context"
        self.generic_visit(node)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    tree = ast.parse(source)
    finder = FindUnusedParameters()
    finder.visit(tree)
