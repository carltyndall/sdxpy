"""
Demonstrate why sets make testing hard: set iteration order is not guaranteed,
so a topological sort that uses sets can produce different orderings across runs.
"""

import sys


def topo_sort_unstable(graph):
    """Topological sort using a set for available nodes (non-deterministic)."""
    # Copy the graph so we don't mutate the original
    remaining = {n: set(deps) for n, deps in graph.items()}
    result = []

    while remaining:
        available = {n for n in remaining if not remaining[n]}

        if not available:
            raise ValueError(f"Circular dependency detected: {set(remaining.keys())}")

        # Extend with set order — unpredictable between runs on some Python impls
        result.extend(available)
        remaining = {
            n: remaining[n] - available
            for n in remaining
            if n not in available
        }

    return result


def topo_sort_stable(graph):
    """Topological sort that sorts available nodes for deterministic output."""
    remaining = {n: set(deps) for n, deps in graph.items()}
    result = []

    while remaining:
        available = {n for n in remaining if not remaining[n]}

        if not available:
            raise ValueError(f"Circular dependency detected: {set(remaining.keys())}")

        # Sort to guarantee deterministic order
        result.extend(sorted(available))
        remaining = {
            n: remaining[n] - available
            for n in remaining
            if n not in available
        }

    return result


def main():
    # A graph where multiple nodes have no dependencies
    graph = {
        "B": [],
        "C": [],
        "A": ["B", "C"],
        "D": [],
    }

    print("Graph:")
    for node, deps in graph.items():
        print(f"  {node} depends on {deps}")

    print("\nUnstable sort (no sorting of available set):")
    order1 = topo_sort_unstable(graph)
    print(f"  Run 1: {order1}")

    # Run multiple times to show we can get different orders
    # (though on CPython 3.7+ set iteration order may appear stable for small sets,
    # the guarantee is not there)
    order2 = topo_sort_unstable(graph)
    print(f"  Run 2: {order2}")

    print("\nStable sort (sorted available nodes):")
    order3 = topo_sort_stable(graph)
    print(f"  Always: {order3}")
    order4 = topo_sort_stable(graph)
    print(f"  Always: {order4}")

    print(f"\nStable results match: {order3 == order4}")

    # Show that set order can differ from sorted order
    s = {"B", "D", "C"}
    print(f"\nSet iteration order: {s} or some permutation")
    print(f"Sorted order: {sorted(s)}")
    print(
        "A test that asserts a specific ordering from set iteration is fragile."
    )


if __name__ == "__main__":
    main()
