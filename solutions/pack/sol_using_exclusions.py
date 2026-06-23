"""Modify the constraint solver to use package exclusions instead of requirements.

Instead of specifying which versions a package *requires*, we specify
which versions it *excludes*.  This inverts the usual dependency model:
if Red 1.2 cannot work with Green 3.1 or 3.2, then Red 1.2 can work with
any *other* version of Green."""

import json
import sys


def compatible_exclusions(exclusions, candidate):
    """Check a candidate combination against exclusion rules.

    *exclusions* maps (package, version) -> {(other_pkg, other_ver), ...}
    meaning "this package+version cannot be installed alongside that
    package+version".
    """
    for pkg_i, ver_i in candidate:
        key_i = (pkg_i, ver_i)
        for pkg_j, ver_j in candidate:
            if pkg_i == pkg_j:
                continue
            key_j = (pkg_j, ver_j)
            if key_i in exclusions and key_j in exclusions[key_i]:
                return False
    return True


def find(manifest, exclusions, remaining, accum, current, count):
    count += 1
    if not remaining:
        accum.append(current)
    else:
        head, tail = remaining[0], remaining[1:]
        for version in manifest[head]:
            candidate = current + [(head, version)]
            if compatible_exclusions(exclusions, candidate):
                count = find(manifest, exclusions, tail, accum, candidate, count)
    return count


def build_exclusions(manifest):
    """Convert a requirements manifest into an exclusions dictionary.

    If package P version V *requires* specific versions of dependency D,
    then all other versions of D are *excluded*.
    """
    exclusions = {}
    for pkg, versions in manifest.items():
        for ver, deps in versions.items():
            # deps can be a dict (version -> list of allowed versions)
            # or an empty list (no dependencies at all).
            if isinstance(deps, list):
                continue
            for dep_pkg, allowed in deps.items():
                all_versions = set(manifest[dep_pkg].keys())
                excluded = all_versions - set(allowed)
                for ev in excluded:
                    exclusions.setdefault((pkg, ver), set()).add((dep_pkg, ev))
    return exclusions


def main():
    manifest = json.load(sys.stdin)
    exclusions = build_exclusions(manifest)
    print("Exclusions generated:")
    for (pkg, ver), excl in sorted(exclusions.items()):
        for e in sorted(excl):
            print(f"  {pkg}.{ver} excludes {e[0]}.{e[1]}")

    all_packages = list(manifest.keys())
    accum = []
    count = find(manifest, exclusions, all_packages, accum, [], 0)

    print(f"\nCandidates examined: {count}")
    print(f"Valid combinations: {len(accum)}")
    for a in accum:
        print(a)


if __name__ == "__main__":
    main()
