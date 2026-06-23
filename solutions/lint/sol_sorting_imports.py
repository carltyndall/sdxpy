"""Report import statements that violate standard sorting rules."""

import ast
import sys


# Standard-library module names as of Python 3.10+.
try:
    STDLIB = sys.stdlib_module_names
except AttributeError:
    # Fallback for older Python versions: a curated subset.
    STDLIB = frozenset({
        "abc", "argparse", "ast", "asyncio", "base64", "collections",
        "copy", "csv", "datetime", "decimal", "functools", "glob",
        "hashlib", "io", "itertools", "json", "math", "os", "pathlib",
        "pickle", "random", "re", "shutil", "sqlite3", "string", "struct",
        "subprocess", "sys", "tempfile", "textwrap", "threading", "time",
        "typing", "unittest", "urllib", "xml", "zipfile",
    })


def _module_key(module_name, is_relative):
    """Return a sort key: (group, module_name) where group is 0=stdlib,
    1=third-party, 2=local."""
    if is_relative:
        return (2, module_name)
    top = module_name.split(".")[0]
    if top in STDLIB:
        return (0, module_name)
    return (1, module_name)


class CheckImports(ast.NodeVisitor):
    """Collect import statements and report ordering violations."""

    def __init__(self):
        super().__init__()
        self._imports = []  # list of (lineno, group, module_name)

    def visit_Import(self, node):
        for alias in node.names:
            self._imports.append(
                (node.lineno, alias.name, False)
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module is None:
            self.generic_visit(node)
            return
        is_relative = node.level is not None and node.level > 0
        self._imports.append(
            (node.lineno, node.module, is_relative)
        )
        self.generic_visit(node)

    def report(self):
        if not self._imports:
            return
        # Sort by line number, then check that group order is non-decreasing
        # and that imports within a group are alphabetical.
        ordered = sorted(self._imports, key=lambda x: x[0])
        prev_key = None
        prev_name = None
        for lineno, name, is_rel in ordered:
            cur_key = _module_key(name, is_rel)
            if prev_key is not None:
                if cur_key < prev_key:
                    print(
                        f"import '{name}' at line {lineno} "
                        f"is out of order (should come before '{prev_name}')"
                    )
                elif (cur_key == prev_key
                      and name.lower() < prev_name.lower()):
                    print(
                        f"import '{name}' at line {lineno} "
                        f"is not in alphabetical order (before '{prev_name}')"
                    )
            prev_key = cur_key
            prev_name = name


if __name__ == "__main__":
    with open(sys.argv[1], "r") as reader:
        source = reader.read()
    tree = ast.parse(source)
    checker = CheckImports()
    checker.visit(tree)
    checker.report()
