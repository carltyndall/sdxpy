import subprocess
import sys
import textwrap
import tempfile
import pathlib


def make_sample_files(directory):
    """Create two small Python files with common problems."""
    buggy = directory / "buggy.py"
    untidy = directory / "untidy.py"

    buggy.write_text(textwrap.dedent("""\
        import os
        import json  # unused

        def do_stuff(x):
            result = x + 1
            return resut  # typo: undefined name

    """))

    untidy.write_text(textwrap.dedent("""\
        def hello():
            print("Hello, world!")



        def goodbye():
            print("Goodbye!")
    """))

    return [buggy, untidy]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        files = make_sample_files(pathlib.Path(tmp))
        for f in files:
            print(f"--- {f.name} ---")
            print(f.read_text())

        print("=== ruff check ===")
        subprocess.run([sys.executable, "-m", "ruff", "check", tmp])


if __name__ == "__main__":
    main()
