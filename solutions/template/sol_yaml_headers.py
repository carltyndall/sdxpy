"""Solution: YAML Headers exercise.

Modify the template expander to handle variables defined in a YAML header
at the top of the page being processed.
"""

import sys
from bs4 import BeautifulSoup

try:
    import yaml
except ImportError:
    yaml = None

from expander import Expander


def parse_yaml_header(text):
    """Extract a YAML frontmatter block delimited by --- lines."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        header = yaml.safe_load(parts[1])
    except Exception:
        header = {}
    return (header if isinstance(header, dict) else {}), parts[2]


def expand_with_yaml(filename, global_vars=None):
    """Expand a template file that may have a YAML header."""
    if global_vars is None:
        global_vars = {}
    with open(filename, "r") as reader:
        raw = reader.read()
    header_vars, body = parse_yaml_header(raw)
    variables = dict(global_vars)
    variables.update(header_vars)
    doc = BeautifulSoup(body, "html.parser")
    expander = Expander(doc.find("html"), variables)
    expander.walk()
    return expander.getResult()


def main():
    if yaml is None:
        print("PyYAML is not installed. Install it with: pip install pyyaml")
        sys.exit(1)

    # Write a temporary file with a YAML header.
    import os
    filename = "sol_yaml_headers_test.html"
    with open(filename, "w") as writer:
        writer.write("---\n")
        writer.write("name: Dorothy Johnson Vaughan\n")
        writer.write("role: mathematician\n")
        writer.write("---\n")
        writer.write("<html><body><p><span z-var=\"name\"/> was a <span z-var=\"role\"/>.</p></body></html>\n")

    result = expand_with_yaml(filename, {"role": "computer"})
    print(result)
    os.remove(filename)


if __name__ == "__main__":
    main()
