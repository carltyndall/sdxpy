"""Generate Z3 constraints from a JSON package manifest.

This automates the manual constraint construction shown in the chapter:
for any manifest it creates Boolean variables, mutual-exclusion rules,
and inter-package dependency constraints, then solves for all valid
combinations."""

import json
import sys

from z3 import And, Bool, Implies, Not, Or, Solver, sat


def generate_constraints(manifest):
    """Return (variables, solver) populated with constraints from the manifest.

    *variables* is a dict mapping (package, version) -> Bool variable.
    The solver already contains the "at least one version per package"
    and mutual-exclusion rules.  Dependency constraints must be added
    by the caller after inspecting the manifest.
    """
    # Create a Bool variable for every package+version pair.
    vars_ = {}
    for pkg, versions in manifest.items():
        for ver in versions:
            vars_[(pkg, ver)] = Bool(f"{pkg}.{ver}")

    solver = Solver()

    # Each package: at least one version must be selected.
    for pkg in manifest:
        pkg_vars = [vars_[(pkg, v)] for v in manifest[pkg]]
        solver.add(Or(*pkg_vars))

    # Mutual exclusion: selecting one version excludes all others.
    for pkg, versions in manifest.items():
        ver_list = list(versions.keys())
        for i, vi in enumerate(ver_list):
            others = [vars_[(pkg, ver_list[j])] for j in range(len(ver_list)) if j != i]
            solver.add(Implies(vars_[(pkg, vi)], Not(Or(*others))))

    # Inter-package dependencies: if P.v is selected then for each
    # dependency D it must be paired with one of the allowed versions.
    for pkg, versions in manifest.items():
        for ver, deps in versions.items():
            for dep_pkg, allowed in deps.items():
                allowed_vars = [vars_[(dep_pkg, av)] for av in allowed]
                solver.add(Implies(vars_[(pkg, ver)], Or(*allowed_vars)))

    return vars_, solver


def find_all_solutions(solver, variables):
    """Enumerate all satisfying models, excluding each one as it is found."""
    everything = list(variables.values())
    solutions = []
    while solver.check() == sat:
        model = solver.model()
        sol = {str(v): bool(model[v]) for v in everything if bool(model[v])}
        solutions.append(sol)
        # Exclude this solution from further searches.
        settings = [v == model[v] for v in everything]
        solver.add(Not(And(*settings)))
    return solutions


def main():
    manifest = json.load(sys.stdin)
    print(f"Loaded manifest with {len(manifest)} packages")

    vars_, solver = generate_constraints(manifest)

    solutions = find_all_solutions(solver, vars_)
    print(f"Found {len(solutions)} solution(s):")
    for i, sol in enumerate(solutions, 1):
        combo = ", ".join(k for k in sorted(sol))
        print(f"  {i}: {combo}")


if __name__ == "__main__":
    main()
