"""Convert build dependencies to Z3 constraints to find legal build orders.

Part 1: the build rules from the build chapter are expressed as Z3 integer
constraints where each node's position in the build sequence must come
after the positions of its dependencies.  The solver then finds a
topological ordering.

Part 2: a circular dependency is introduced and the solver correctly
reports that no model exists."""

import json
import sys

from z3 import And, Distinct, Implies, Int, IntSort, Solver, sat


def find_build_order(config):
    """Return a legal build order (list of node names) for *config*.

    *config* is a dict like {"A": {"depends": ["B"], "rule": "..."}}.
    Returns None when a circular dependency makes ordering impossible.
    """
    nodes = list(config.keys())
    n = len(nodes)

    # Assign each node an integer position in the build order (0..n-1).
    pos = {node: Int(f"pos_{node}") for node in nodes}

    solver = Solver()

    # All positions are distinct and in range [0, n-1].
    solver.add(Distinct(*pos.values()))
    for node in nodes:
        solver.add(pos[node] >= 0)
        solver.add(pos[node] < n)

    # Dependency constraint: if A depends on B then pos(A) > pos(B).
    for node, info in config.items():
        for dep in info.get("depends", []):
            solver.add(pos[node] > pos[dep])

    if solver.check() != sat:
        return None

    model = solver.model()
    # Sort nodes by their position in the model.
    ordered = sorted(nodes, key=lambda node: model[pos[node]].as_long())
    return ordered


def main():
    # ---- Part 1: acyclic build rules ---------------------------------------
    config = {
        "A": {"depends": ["B", "C"], "rule": "build A"},
        "B": {"depends": ["D"], "rule": "build B"},
        "C": {"depends": ["D"], "rule": "build C"},
        "D": {"depends": [], "rule": "build D"},
    }
    print("Part 1: acyclic build dependencies")
    order = find_build_order(config)
    if order:
        for step, node in enumerate(order, 1):
            print(f"  {step}. {node}  ({config[node]['rule']})")
    else:
        print("  No legal build order found.")

    # ---- Part 2: introduce a circular dependency ---------------------------
    print()
    print("Part 2: adding a circular dependency (A -> B -> A)")
    circular = dict(config)
    circular["B"]["depends"] = circular["B"]["depends"] + ["A"]
    order = find_build_order(circular)
    if order:
        print("  Unexpectedly found an order:", order)
    else:
        print("  Z3 correctly reports UNSAT (no model exists).")


if __name__ == "__main__":
    main()
