"""Report assignments that are immediately overwritten."""

import ast
import sys


class FindRedundantAssignments(ast.NodeVisitor):
    """Find variables assigned a value that is overwritten before being read."""

    def visit_Module(self, node):
        self._check_body(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self._check_body(node.body)
        self.generic_visit(node)

    def _check_body(self, body):
        """Walk a list of statements looking for back-to-back assignments."""
        last_targets = {}
        last_lineno = {}
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name in last_targets:
                            print(
                                f"redundant assignment to {name} "
                                f"at line {last_lineno[name]} "
                                f"(overwritten at line {stmt.lineno})"
                            )
                # Record this statement's targets for the next comparison.
                last_targets = {}
                last_lineno = {}
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        last_targets[target.id] = True
                        last_lineno[target.id] = stmt.lineno
            elif isinstance(stmt, ast.Expr):
                # An expression statement might read variables, so clear
                # our tracking: the previous assignment is no longer
                # "immediately" overwritten.
                last_targets = {}
                last_lineno = {}
            # Other statement types (loops, conditionals, etc.) also
            # break the chain of immediate overwrites.
            else:
                last_targets = {}
                last_lineno = {}


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    tree = ast.parse(source)
    finder = FindRedundantAssignments()
    finder.visit(tree)
