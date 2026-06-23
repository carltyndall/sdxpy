"""Check that class, function, and variable names follow conventions."""

import ast
import re
import sys

# CamelCase: starts with an uppercase letter, contains only letters and digits.
CAMEL_CASE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
# pothole_case (snake_case): lowercase letters, digits, and underscores.
POTHOLE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")


class CheckNames(ast.NodeVisitor):
    """Report names that violate CamelCase (classes) or pothole_case (others)."""

    def visit_ClassDef(self, node):
        if not CAMEL_CASE.match(node.name):
            print(
                f"{node.name} at line {node.lineno}: "
                "class names should use CamelCase"
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if not POTHOLE_CASE.match(node.name):
            print(
                f"{node.name} at line {node.lineno}: "
                "function names should use pothole_case"
            )
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if not POTHOLE_CASE.match(target.id):
                    print(
                        f"{target.id} at line {node.lineno}: "
                        "variable names should use pothole_case"
                    )
        self.generic_visit(node)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    tree = ast.parse(source)
    checker = CheckNames()
    checker.visit(tree)
