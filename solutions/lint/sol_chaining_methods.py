"""Demonstrate chained method injection with recursion signalling."""

import ast
import sys


class BlankNodeVisitor(ast.NodeVisitor):
    """A NodeVisitor subclass with no custom visit methods (yet)."""
    pass


def inject_chained(cls, method_name, new_func):
    """Add *new_func* as *method_name* on *cls*, chaining any existing method.

    When the resulting method is called it invokes the previously registered
    method first, then the new one.  Each method receives the visitor instance
    and the AST node as usual.
    """
    old_func = getattr(cls, method_name, None)

    def chained(self, node):
        if old_func is not None:
            old_func(self, node)
        new_func(self, node)

    setattr(cls, method_name, chained)


def inject_signalling(cls, method_name, new_func):
    """Like *inject_chained*, but each method can signal whether it already
    handled recursion by setting ``self._recursion_handled`` to ``True``.
    When a preceding method sets this flag the remaining methods in the chain
    skip their own recursive descent (though they still do their own checks).
    """
    old_func = getattr(cls, method_name, None)

    def chained(self, node):
        self._recursion_handled = False
        if old_func is not None:
            old_func(self, node)
        if not self._recursion_handled:
            new_func(self, node)

    setattr(cls, method_name, chained)


# --- demonstration helpers --------------------------------------------------

def print_name(self, node):
    """Emit the name of the variable being visited."""
    print(f"visit_Name: {node.id}")


def count_name_length(self, node):
    """Emit the length of the variable name, then handle recursion so no
    other method in the chain needs to recurse."""
    print(f"  name length: {len(node.id)}")
    self.generic_visit(node)
    self._recursion_handled = True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python sol_chaining_methods.py FILE [--signalling]",
              file=sys.stderr)
        sys.exit(1)

    mode = "--signalling" if "--signalling" in sys.argv else "--chained"

    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    tree = ast.parse(source)

    if mode == "--signalling":
        inject_signalling(BlankNodeVisitor, "visit_Name", print_name)
        inject_signalling(BlankNodeVisitor, "visit_Name", count_name_length)
        print("--- signalling mode ---")
    else:
        inject_chained(BlankNodeVisitor, "visit_Name", print_name)
        inject_chained(BlankNodeVisitor, "visit_Name", count_name_length)
        print("--- chained mode ---")

    finder = BlankNodeVisitor()
    finder.visit(tree)
