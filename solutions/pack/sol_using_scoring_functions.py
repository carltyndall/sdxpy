"""Scoring function that measures version distance to prefer newer packages.

The distance between two versions is:
- 100 times the difference in major version numbers;
- 10 times the difference in minor version numbers if the major numbers agree;
- the difference in patch numbers if both major and minor numbers agree.

This script uses the scoring function to measure the total distance between
a candidate set of package versions and the set containing the most recent
version of each package."""


def parse_version(v):
    """Parse a version string like '3' or '2.1' into (major, minor, patch)."""
    parts = [int(x) for x in v.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def version_distance(a, b):
    """Compute the weighted distance between two version strings."""
    ma, mi_a, pa = parse_version(a)
    mb, mi_b, pb = parse_version(b)
    if ma != mb:
        return 100 * abs(ma - mb)
    if mi_a != mi_b:
        return 10 * abs(mi_a - mi_b)
    return abs(pa - pb)


def total_distance(candidate, newest):
    """Return the sum of per-package distances between two dicts.

    *candidate* and *newest* are dicts mapping package name to version
    string.  Only packages present in both are compared.
    """
    total = 0
    for pkg in candidate:
        if pkg in newest:
            total += version_distance(candidate[pkg], newest[pkg])
    return total


def main():
    # Using the triple.json example: A has versions 1,2,3; B has 1,2,3; C has 1,2.
    newest = {"A": "3", "B": "3", "C": "2"}

    # The three valid combinations from the chapter.
    candidates = [
        {"A": "3", "B": "3", "C": "2"},
        {"A": "3", "B": "2", "C": "2"},
        {"A": "2", "B": "2", "C": "2"},
    ]

    for i, cand in enumerate(candidates):
        d = total_distance(cand, newest)
        print(f"Candidate {i + 1}: {cand}  distance={d}")

    print()
    print("Lower distance means closer to the latest-everything ideal.")
    print("But is 'closest to newest' really what we want?")
    print("A package manager might prefer the oldest compatible set")
    print("if stability matters more than freshness.")


if __name__ == "__main__":
    main()
