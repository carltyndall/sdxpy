import csv
import sys


def read_manifest(path):
    records = {}
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records[row["filename"]] = row["hash"]
    return records


def compare_manifests(old_path, new_path):
    old = read_manifest(old_path)
    new = read_manifest(new_path)

    old_names = set(old.keys())
    new_names = set(new.keys())
    old_hashes = set(old.values())
    new_hashes = set(new.values())

    name_to_hash_old = {h: [] for h in old_hashes}
    for name, h in old.items():
        name_to_hash_old[h].append(name)
    name_to_hash_new = {h: [] for h in new_hashes}
    for name, h in new.items():
        name_to_hash_new[h].append(name)

    modified = []
    for name in old_names & new_names:
        if old[name] != new[name]:
            modified.append(name)

    renamed = []
    common_hashes = old_hashes & new_hashes
    for h in common_hashes:
        old_files = set(name_to_hash_old[h])
        new_files = set(name_to_hash_new[h])
        if old_files != new_files:
            renamed.append((h, sorted(old_files), sorted(new_files)))

    added = []
    for name in new_names - old_names:
        h = new[name]
        if h not in old_hashes:
            added.append(name)

    deleted = []
    for name in old_names - new_names:
        h = old[name]
        if h not in new_hashes:
            deleted.append(name)

    return modified, renamed, added, deleted


def report(modified, renamed, added, deleted):
    if modified:
        print("Modified (same name, different hash):")
        for name in sorted(modified):
            print(f"    {name}")
    if renamed:
        print("Renamed (same hash, different name):")
        for h, old_names, new_names in sorted(renamed):
            print(f"    hash {h}:")
            print(f"        was: {', '.join(old_names)}")
            print(f"        now: {', '.join(new_names)}")
    if added:
        print("Added (in second manifest only):")
        for name in sorted(added):
            print(f"    {name}")
    if deleted:
        print("Deleted (in first manifest only):")
        for name in sorted(deleted):
            print(f"    {name}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: compare_manifests.py old.csv new.csv"
    modified, renamed, added, deleted = compare_manifests(sys.argv[1], sys.argv[2])
    report(modified, renamed, added, deleted)
