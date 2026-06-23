"""Search packages starting with those that have the fewest available versions.

The idea is reminiscent of the "most constrained variable" heuristic in
constraint programming: by tackling packages with fewer choices first we
expect to prune the search space earlier and examine fewer candidates."""

import json
import sys


def compatible(manifest, candidate):
    for package_i, version_i in candidate:
        lookup_i = manifest[package_i][version_i]
        for package_j, version_j in candidate:
            if package_i == package_j:
                continue
            if package_j not in lookup_i:
                continue
            if version_j not in lookup_i[package_j]:
                return False
    return True


def find(manifest, remaining, accum, current, count):
    count += 1
    if not remaining:
        accum.append(current)
    else:
        head, tail = remaining[0], remaining[1:]
        for version in manifest[head]:
            candidate = current + [(head, version)]
            if compatible(manifest, candidate):
                count = find(manifest, tail, accum, candidate, count)
    return count


def main():
    manifest = json.load(sys.stdin)
    all_packages = list(manifest.keys())

    # Sort by number of available versions (fewest first).
    all_packages.sort(key=lambda p: len(manifest[p]))

    print(f"Package order (fewest versions first): {all_packages}")

    accum = []
    count = find(manifest, all_packages, accum, [], 0)

    print(f"Candidates examined: {count}")
    print(f"Valid combinations: {len(accum)}")
    for a in accum:
        print(a)


if __name__ == "__main__":
    main()
