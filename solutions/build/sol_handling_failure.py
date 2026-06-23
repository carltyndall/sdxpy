"""
Build manager that supports rules that can succeed or fail, and continues
building unrelated targets when a rule fails. Failure propagates transitively:
if C fails, anything that depends on C (directly or indirectly) is not built.
"""

import json
import sys


class BuildFailure(Exception):
    """Raised when a build rule explicitly fails."""


class BuildResilient:
    def build(self, config):
        config = self._configure(config)
        ordered = self._topo_sort(config)
        actions = []
        failed = set()

        for node in ordered:
            # Any node whose dependencies intersect the failed set is skipped
            # and marked as failed itself so dependents are also skipped.
            if failed & config[node].get("depends", set()):
                failed.add(node)
                continue

            try:
                self._refresh(config, node, actions)
            except BuildFailure:
                failed.add(node)

        return actions

    def _refresh(self, config, node, actions):
        assert node in config, f"Unknown node {node}"
        rule_info = config[node]
        if rule_info.get("fail", False):
            raise BuildFailure(f"Rule for {node} explicitly failed")
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
        result.setdefault("fail", False)
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
    # Test 1: normal build with no failures
    print("=== Test 1: No failures ===")
    config1 = {
        "A": {"depends": ["B"], "rule": "build A", "fail": False},
        "B": {"depends": [], "rule": "build B", "fail": False},
    }
    try:
        result = BuildResilient().build(config1)
        print(f"Actions: {result}")
    except (ValueError, BuildFailure) as e:
        print(f"Error: {e}")

    # Test 2: a rule that fails, but nothing depends on it
    print("\n=== Test 2: Isolated failure ===")
    config2 = {
        "A": {"depends": [], "rule": "build A", "fail": False},
        "B": {"depends": [], "rule": "build B", "fail": True},
        "C": {"depends": [], "rule": "build C", "fail": False},
    }
    try:
        result = BuildResilient().build(config2)
        print(f"Actions: {result}")
    except (ValueError, BuildFailure) as e:
        print(f"Error: {e}")

    # Test 3: a failing rule with a dependent — dependent should be skipped
    print("\n=== Test 3: Dependent skipped on failure ===")
    config3 = {
        "A": {"depends": ["B"], "rule": "build A", "fail": False},
        "B": {"depends": [], "rule": "build B", "fail": True},
        "C": {"depends": [], "rule": "build C", "fail": False},
    }
    try:
        result = BuildResilient().build(config3)
        print(f"Actions: {result}")
    except (ValueError, BuildFailure) as e:
        print(f"Error: {e}")

    # Test 4: transitive failure — A depends on B which depends on C (failing)
    print("\n=== Test 4: Transitive failure ===")
    config4 = {
        "A": {"depends": ["B"], "rule": "build A", "fail": False},
        "B": {"depends": ["C"], "rule": "build B", "fail": False},
        "C": {"depends": [], "rule": "build C", "fail": True},
        "D": {"depends": [], "rule": "build D", "fail": False},
    }
    try:
        result = BuildResilient().build(config4)
        print(f"Actions: {result}")
    except (ValueError, BuildFailure) as e:
        print(f"Error: {e}")

    # Test 5: circular dependency is still caught
    print("\n=== Test 5: Circular dependency ===")
    config5 = {
        "A": {"depends": ["B"], "rule": "build A", "fail": False},
        "B": {"depends": ["A"], "rule": "build B", "fail": False},
    }
    try:
        result = BuildResilient().build(config5)
        print(f"Actions: {result}")
    except (ValueError, BuildFailure) as e:
        print(f"Error (expected): {e}")


if __name__ == "__main__":
    main()
