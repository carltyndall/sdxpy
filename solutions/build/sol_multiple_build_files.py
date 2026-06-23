"""
Build manager that allows one build file to import definitions and
dependencies from another. Imports are specified with an "import" key
that lists paths to other build files. Circular imports are detected
and reported.
"""

import json
import os
import sys


class BuildImport:
    def build(self, config_path):
        """Build from a config file path. The file may import others."""
        config = self._load_with_imports(config_path)
        config = self._configure(config)
        ordered = self._topo_sort(config)
        actions = []

        for node in ordered:
            self._refresh(config, node, actions)

        return actions

    def _load_with_imports(self, config_path, seen=None):
        """Recursively load a config file and its imports.
        Returns a merged dict with all targets."""
        if seen is None:
            seen = set()

        # Resolve to absolute path for cycle detection
        abs_path = os.path.abspath(config_path)

        if abs_path in seen:
            raise ValueError(
                f"Circular import detected: {abs_path} already loaded "
                f"(chain: {' -> '.join(seen)} -> {abs_path})"
            )

        seen.add(abs_path)

        with open(config_path, "r") as f:
            data = json.load(f)

        imports = data.pop("import", [])
        merged = {}

        # Load imports first so the current file can override them
        for import_path in imports:
            # Resolve relative paths against the directory of the current file
            base_dir = os.path.dirname(abs_path)
            resolved = os.path.normpath(
                os.path.join(base_dir, import_path)
            )

            imported = self._load_with_imports(resolved, seen.copy())
            for name, details in imported.items():
                if name in merged:
                    print(
                        f"Warning: target '{name}' from {import_path} "
                        f"overridden by earlier import"
                    )
                merged[name] = details

        # Add targets from this file (they override imports)
        for name, details in data.items():
            if name in merged:
                print(
                    f"Note: target '{name}' in {config_path} "
                    f"overrides imported definition"
                )
            merged[name] = details

        return merged

    def _refresh(self, config, node, actions):
        assert node in config, f"Unknown node {node}"
        actions.append(config[node]["rule"])

    def _must(self, condition, message):
        if not condition:
            raise ValueError(message)

    def _configure(self, config):
        known = set(config.keys())
        return {
            n: self._check(n, d, known)
            for n, d in config.items()
        }

    def _check(self, name, details, known):
        self._check_keys(name, details)
        depends = set(details["depends"])
        self._must(
            depends.issubset(known),
            f"Unknown depends for {name}",
        )
        result = details.copy()
        result["depends"] = depends
        return result

    def _check_keys(self, name, details):
        self._must(
            "rule" in details,
            f"Missing rule for {name}",
        )
        self._must(
            "depends" in details,
            f"Missing depends for {name}",
        )

    def _topo_sort(self, config):
        graph = {n: config[n]["depends"] for n in config}
        result = []
        while graph:
            available = {n for n in graph if not graph[n]}
            self._must(
                available,
                f"Circular graph {list(graph.keys())}",
            )
            result.extend(sorted(available))
            graph = {
                n: graph[n] - available
                for n in graph
                if n not in available
            }
        return result


def main():
    import tempfile
    import shutil

    tmpdir = tempfile.mkdtemp()

    # Create a base library of rules
    lib_path = os.path.join(tmpdir, "lib.json")
    lib_config = {
        "util.o": {
            "depends": ["util.c"],
            "rule": "gcc -c util.c",
        },
        "util.c": {
            "depends": [],
            "rule": "echo 'void util() {}' > util.c",
        },
    }
    with open(lib_path, "w") as f:
        json.dump(lib_config, f, indent=2)

    # Create a main build file that imports the library
    main_path = os.path.join(tmpdir, "build.json")
    main_config = {
        "import": ["lib.json"],
        "program.exe": {
            "depends": ["main.o", "util.o"],
            "rule": "gcc -o program.exe main.o util.o",
        },
        "main.o": {
            "depends": ["main.c"],
            "rule": "gcc -c main.c",
        },
        "main.c": {
            "depends": [],
            "rule": "echo 'int main() { return 0; }' > main.c",
        },
    }
    with open(main_path, "w") as f:
        json.dump(main_config, f, indent=2)

    print(f"Library ({lib_path}):")
    print(json.dumps(lib_config, indent=2))

    print(f"\nMain build file ({main_path}):")
    print(json.dumps(main_config, indent=2))

    print("\n=== Building with imports ===")
    builder = BuildImport()
    actions = builder.build(main_path)
    print(f"Actions: {actions}")

    # Demonstrate circular import detection
    circular_path = os.path.join(tmpdir, "circular.json")
    circular_config = {
        "import": ["self_ref.json"],
        "A": {"depends": [], "rule": "build A"},
    }
    with open(circular_path, "w") as f:
        json.dump(circular_config, f, indent=2)

    self_ref_path = os.path.join(tmpdir, "self_ref.json")
    # self_ref imports circular.json, creating a cycle
    self_ref_config = {
        "import": ["circular.json"],
        "B": {"depends": ["A"], "rule": "build B"},
    }
    with open(self_ref_path, "w") as f:
        json.dump(self_ref_config, f, indent=2)

    print("\n=== Circular import detection ===")
    try:
        builder.build(circular_path)
        print("ERROR: should have detected circular import")
    except ValueError as e:
        print(f"Correctly detected: {e}")

    # Cleanup
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
