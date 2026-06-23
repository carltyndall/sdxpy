"""Compare and sort semantic version specifiers.

Remember that 2.1 is greater than 1.99: the major, minor, and patch
components are compared numerically, not as decimal fractions."""

import sys


def parse_semver(version_str):
    """Parse a semantic version string into a tuple of integers.

    Returns a tuple (major, minor, patch) for straightforward numeric
    comparison.  Versions with fewer than three components are padded
    with zeros.
    """
    parts = version_str.split(".")
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0
    return (major, minor, patch)


def sort_versions(versions):
    """Sort a list of semantic version strings in ascending order."""
    return sorted(versions, key=parse_semver)


def main():
    examples = ["1.99", "2.0", "2.1", "1.0", "1.0.1", "1.0.0", "1.99.1"]
    print("Original:", examples)
    print("Sorted:  ", sort_versions(examples))

    # The key insight: 2.1 > 1.99 because we compare (2,1,0) vs (1,99,0).
    assert sort_versions(["2.1", "1.99"]) == ["1.99", "2.1"]
    print("Verified: 2.1 > 1.99")


if __name__ == "__main__":
    main()
