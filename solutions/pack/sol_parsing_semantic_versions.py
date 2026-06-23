"""Parse a subset of the semantic versioning specification.

This parser handles MAJOR.MINOR.PATCH with optional pre-release labels
and build metadata, as described at https://semver.org."""

import re


# Semver 2.0.0 core pattern: MAJOR.MINOR.PATCH with optional pre-release
# (dotted alphanumeric identifiers after '-') and optional build metadata
# (dotted alphanumeric identifiers after '+').
_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)"
    r"\.(?P<minor>0|[1-9]\d*)"
    r"\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


class SemVer:
    """A parsed semantic version with ordering support."""

    def __init__(self, version_str):
        m = _SEMVER_RE.match(version_str)
        if not m:
            raise ValueError(f"invalid semantic version: {version_str!r}")
        self.major = int(m.group("major"))
        self.minor = int(m.group("minor"))
        self.patch = int(m.group("patch"))
        self.prerelease = m.group("prerelease")
        self.build = m.group("build")

    def __repr__(self):
        return f"SemVer({self.major}.{self.minor}.{self.patch})"

    def __lt__(self, other):
        a = (self.major, self.minor, self.patch)
        b = (other.major, other.minor, other.patch)
        if a != b:
            return a < b
        # A version without a pre-release label sorts after one with one.
        if self.prerelease is None and other.prerelease is not None:
            return False
        if self.prerelease is not None and other.prerelease is None:
            return True
        if self.prerelease is not None and other.prerelease is not None:
            return self._cmp_prerelease(other) < 0
        return False

    def __eq__(self, other):
        return (self.major, self.minor, self.patch, self.prerelease) == (
            other.major, other.minor, other.patch, other.prerelease)

    def _cmp_prerelease(self, other):
        """Compare two pre-release identifiers dot-segment by dot-segment."""
        a_parts = self.prerelease.split(".")
        b_parts = other.prerelease.split(".")
        for pa, pb in zip(a_parts, b_parts):
            if pa.isdigit() and pb.isdigit():
                if int(pa) != int(pb):
                    return -1 if int(pa) < int(pb) else 1
            elif pa.isdigit():
                return -1  # numeric < alphanumeric
            elif pb.isdigit():
                return 1
            else:
                if pa != pb:
                    return -1 if pa < pb else 1
        return -1 if len(a_parts) < len(b_parts) else (1 if len(a_parts) > len(b_parts) else 0)


def parse_versions(text):
    """Parse a string containing one version per line; return sorted SemVer list."""
    versions = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            versions.append(SemVer(line))
    versions.sort()
    return versions


def main():
    sample = """\
1.0.0-alpha
1.0.0-alpha.1
1.0.0-beta
1.0.0
2.0.0
1.9.9
1.10.0
1.0.0+build.1"""
    parsed = parse_versions(sample)
    for v in parsed:
        prerelease = f"-{v.prerelease}" if v.prerelease else ""
        build = f"+{v.build}" if v.build else ""
        print(f"{v.major}.{v.minor}.{v.patch}{prerelease}{build}")


if __name__ == "__main__":
    main()
