"""
Build manager with dry-run support. A dry run shows which rules would be
executed without actually executing them.
"""

import json
import sys


class BuildDryRun:
    def build(self, config, dry_run=False):
        config = self._configure(config)
        ordered = self._topo_sort(config)
        actions = []

        for node in ordered:
            if self._needs_update(config, node):
                action = config[node]["rule"]
                if dry_run:
                    print(f"[DRY RUN] would execute: {action}")
                else:
                    self._refresh(config, node, actions)

        return actions

    def _needs_update(self, config, node):
        """Hook for subclasses to determine staleness.
        The base implementation always returns True (always build)."""
        return True

    def _refresh(self, config, node, actions):
        assert node in config, f"Unknown node {node}"
        print(f"[BUILD] executing: {config[node]['rule']}")
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
    config = {
        "A": {"depends": ["B"], "rule": "build A"},
        "B": {"depends": ["C"], "rule": "build B"},
        "C": {"depends": [], "rule": "build C"},
    }

    builder = BuildDryRun()

    print("=== Dry run ===")
    print("(These would be the actions, in order:)")
    result_dry = builder.build(config, dry_run=True)
    print(f"Returned actions (empty — nothing was actually built): {result_dry}")

    print("\n=== Actual build ===")
    result_real = builder.build(config, dry_run=False)
    print(f"Returned actions (these were built): {result_real}")


if __name__ == "__main__":
    main()
