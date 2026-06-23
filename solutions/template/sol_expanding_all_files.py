"""Solution: Expanding All Files exercise.

Write a program expand_all.py that takes two directory names as
command-line arguments and builds a website in the second directory
by expanding all HTML files found in the first or its subdirectories.
"""

import json
import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from expander import Expander


def expand_file(source_path, dest_path, variables):
    """Read, expand, and write a single HTML file."""
    with open(source_path, "r") as reader:
        doc = BeautifulSoup(reader.read(), "html.parser")
        template = doc.find("html")
    expander = Expander(template, variables)
    expander.walk()
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as writer:
        writer.write(expander.getResult())


def expand_all(src_dir, dst_dir, variables):
    """Walk src_dir, expand every .html file, and write to dst_dir."""
    src_dir = os.path.abspath(src_dir)
    dst_dir = os.path.abspath(dst_dir)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if not filename.endswith(".html"):
                continue
            src_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(src_path, src_dir)
            dst_path = os.path.join(dst_dir, rel_path)
            print(f"Expanding {rel_path} -> {dst_path}")
            expand_file(src_path, dst_path, variables)


def main():
    if len(sys.argv) < 3:
        print("Usage: sol_expanding_all_files.py src_dir dst_dir [vars.json]")
        sys.exit(1)
    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]
    variables = {}
    if len(sys.argv) >= 4:
        with open(sys.argv[3], "r") as reader:
            variables = json.load(reader)
    expand_all(src_dir, dst_dir, variables)


if __name__ == "__main__":
    main()
