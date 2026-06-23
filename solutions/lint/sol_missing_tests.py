"""Report functions that are defined but never called in the test file."""

import ast
import sys


def collect_functions(tree):
    """Return a set of top-level function names defined in the AST."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            names.add(node.name)
    return names


def collect_calls(tree):
    """Return a set of function names called in the AST."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                # Track method calls like obj.method(...)
                names.add(node.func.attr)
    return names


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python sol_missing_tests.py SOURCE TESTFILE", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    source_tree = ast.parse(source)
    defined = collect_functions(source_tree)

    with open(sys.argv[2], "r") as reader:
        test_source = reader.read()
    test_tree = ast.parse(test_source)
    called = collect_calls(test_tree)

    missing = defined - called
    if missing:
        for name in sorted(missing):
            print(f"{name} is never called in tests")
    else:
        print("every defined function is called in the test file")
