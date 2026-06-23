"""
Build manager that can read and merge multiple build configuration files.
When two files specify rules for the same target, the last one read wins.
"""

import json
import sys


class BuildMerge:
    def build(self, config):
        config = self._configure(config)
        ordered = self._topo_sort(config)
        actions = []
        for node in ordered:
            self._refresh(config, node, actions)
        return actions

    def build_from_files(self, config_files):
        """Read and merge multiple configuration files."""
        merged = {}
        conflicts = []

        for path in config_files:
            with open(path, "r") as reader:
                part = json.load(reader)

            for name, details in part.items():
                if name in merged:
                    conflicts.append(
                        f"Target '{name}' in {path} overrides "
                        f"previous definition"
                    )
                merged[name] = details

        if conflicts:
            print("Conflicts detected:")
            for c in conflicts:
                print(f"  - {c}")

        return self.build(merged)

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
    import os

    # Write two temporary config files
    tmpdir = tempfile.mkdtemp()

    file1_path = os.path.join(tmpdir, "config1.json")
    file2_path = os.path.join(tmpdir, "config2.json")

    config1 = {
        "A": {"depends": ["B"], "rule": "build A from file1"},
        "B": {"depends": [], "rule": "build B"},
    }

    config2 = {
        "C": {"depends": ["B"], "rule": "build C from file2"},
    }

    with open(file1_path, "w") as f:
        json.dump(config1, f)

    with open(file2_path, "w") as f:
        json.dump(config2, f)

    print(f"File 1 ({file1_path}):")
    print(json.dumps(config1, indent=2))

    print(f"\nFile 2 ({file2_path}):")
    print(json.dumps(config2, indent=2))

    print("\nMerged build result:")
    builder = BuildMerge()
    actions = builder.build_from_files([file1_path, file2_path])
    print(f"  Actions: {actions}")

    # Demonstrate conflict when two files define the same target
    config3 = {
        "A": {"depends": [], "rule": "build A from file3 (overrides)"},
    }

    file3_path = os.path.join(tmpdir, "config3.json")
    with open(file3_path, "w") as f:
        json.dump(config3, f)

    print(f"\nFile 3 ({file3_path}) redefines A:")
    print(json.dumps(config3, indent=2))

    print("\nMerged with conflict (last wins):")
    actions = builder.build_from_files([file1_path, file2_path, file3_path])
    print(f"  Actions: {actions}")

    # Cleanup
    for p in [file1_path, file2_path, file3_path]:
        os.remove(p)
    os.rmdir(tmpdir)


if __name__ == "__main__":
    main()
