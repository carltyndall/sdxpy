"""Demonstrate calendar-based versioning and compare it to semver.

Calendar-based versions (often called "CalVer") use dates rather than
semantic meanings to number releases: 2023.1 might be the first release
of 2023, 2024.2 the second release of 2024, and so on."""

from datetime import date


def generate_calver(year, release_number):
    """Return a CalVer string for a given year and release number."""
    return f"{year}.{release_number}"


def next_calver(current):
    """Advance a CalVer string to the next logical release."""
    year_str, num_str = current.split(".")
    year = int(year_str)
    num = int(num_str)
    if num >= 4:  # arbitrary: assume 4 releases per year
        return f"{year + 1}.1"
    return f"{year}.{num + 1}"


def sort_calver(versions):
    """Sort CalVer strings chronologically.

    This is simpler than semver sorting because the date components are
    naturally ordered: a later year is always greater, and a later
    release number within the same year is always greater.
    """
    def key(v):
        year_str, num_str = v.split(".")
        return (int(year_str), int(num_str))
    return sorted(versions, key=key)


def main():
    releases = ["2023.1", "2024.2", "2023.3", "2024.1", "2022.4"]
    print("Unsorted:", releases)
    print("Sorted:  ", sort_calver(releases))
    print()

    current = "2024.1"
    for _ in range(6):
        print(current)
        current = next_calver(current)

    print()
    print("CalVer advantages:")
    print("- Easy to tell how old a release is at a glance.")
    print("- No arguments about what constitutes a 'major' change.")
    print()
    print("CalVer disadvantages:")
    print("- No signal about backward compatibility from the version alone.")
    print("- Security patches may get lost among scheduled releases.")
    print("- Harder to express dependency ranges like '>=2.0, <3.0'.")


if __name__ == "__main__":
    main()
