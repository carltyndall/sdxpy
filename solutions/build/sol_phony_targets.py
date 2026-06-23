"""
Build manager with support for phony targets. A phony target is one that
doesn't correspond to an actual file — it's a convenient label for running
commands like tests or style checks.
"""

import json
import sys


class BuildPhony:
    def build(self, config):
        config = self._configure(config)
        ordered = self._topo_sort(config)
        actions = []

        for node in ordered:
            self._refresh(config, node, actions)

        return actions

    def _refresh(self, config, node, actions):
        assert node in config, f"Unknown node {node}"
        rule_info = config[node]

        # Phony targets always run (no file to check staleness against)
        if rule_info.get("phony", False):
            print(f"[PHONY] executing: {rule_info['rule']}")

        actions.append(rule_info["rule"])

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
        depends = set(details.get("depends", []))
        self._must(
            depends.issubset(known),
            f"Unknown depends for {name}",
        )
        result = details.copy()
        result["depends"] = depends
        result.setdefault("phony", False)
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
    # A build config with a phony "test" target
    config = {
        "test": {
            "depends": ["program.exe"],
            "rule": "pytest tests/",
            "phony": True,
        },
        "program.exe": {
            "depends": ["main.o", "util.o"],
            "rule": "gcc -o program.exe main.o util.o",
        },
        "main.o": {
            "depends": ["main.c"],
            "rule": "gcc -c main.c",
        },
        "util.o": {
            "depends": ["util.c"],
            "rule": "gcc -c util.c",
        },
        "main.c": {
            "depends": [],
            "rule": "echo 'int main() { return 0; }' > main.c",
        },
        "util.c": {
            "depends": [],
            "rule": "echo 'void util() {}' > util.c",
        },
    }

    builder = BuildPhony()
    print("=== Build with phony target ===")
    actions = builder.build(config)
    print(f"\nAll actions: {actions}")

    # Show that phony targets are marked and always run
    print("\nPhony targets in config:")
    for name, details in config.items():
        if details.get("phony"):
            print(f"  {name}: '{details['rule']}' (phony)")


if __name__ == "__main__":
    main()
