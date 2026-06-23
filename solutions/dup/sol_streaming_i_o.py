"""Find duplicate files using SHA-256 with streaming I/O."""

import sys
from hashlib import sha256


def find_groups(filenames):
    groups = {}
    for fn in filenames:
        hasher = sha256()
        with open(fn, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                hasher.update(chunk)
        hash_code = hasher.hexdigest()
        if hash_code not in groups:
            groups[hash_code] = set()
        groups[hash_code].add(fn)
    return groups


if __name__ == "__main__":
    groups = find_groups(sys.argv[1:])
    for filenames in groups.values():
        print(", ".join(sorted(filenames)))
