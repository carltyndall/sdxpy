import csv
import shutil
import sys
from pathlib import Path

from hash_all import hash_all

COUNTER_FILE = "backup_counter.txt"


def next_counter(backup_dir):
    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    counter_path = Path(backup_dir, COUNTER_FILE)
    if counter_path.exists():
        with open(counter_path, "r") as f:
            count = int(f.read().strip()) + 1
    else:
        count = 1
    with open(counter_path, "w") as f:
        f.write(str(count))
    return f"{count:08d}"


def backup(source_dir, backup_dir):
    manifest = hash_all(source_dir)
    backup_num = next_counter(backup_dir)
    write_manifest(backup_dir, backup_num, manifest)
    copy_files(source_dir, backup_dir, manifest)
    return manifest


def write_manifest(backup_dir, number, manifest):
    backup_dir = Path(backup_dir)
    manifest_file = Path(backup_dir, f"{number}.csv")
    with open(manifest_file, "w", newline="") as raw:
        writer = csv.writer(raw)
        writer.writerow(["filename", "hash"])
        writer.writerows(manifest)


def copy_files(source_dir, backup_dir, manifest):
    for (filename, hash_code) in manifest:
        source_path = Path(source_dir, filename)
        backup_path = Path(backup_dir, f"{hash_code}.bck")
        if not backup_path.exists():
            shutil.copy(source_path, backup_path)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: sequencing_backups.py source_dir backup_dir"
    backup(sys.argv[1], sys.argv[2])
