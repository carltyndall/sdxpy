import csv
import json
import os
import shutil
import sys
from pathlib import Path

from hash_all import hash_all


def backup(source_dir, backup_dir, fmt="csv"):
    manifest = hash_all(source_dir)
    timestamp = current_time()
    username = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
    write_manifest(backup_dir, timestamp, manifest, username, fmt)
    copy_files(source_dir, backup_dir, manifest)
    return manifest


def current_time():
    import time
    return f"{time.time()}".split(".")[0]


def write_manifest(backup_dir, timestamp, manifest, username, fmt="csv"):
    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    manifest_file = Path(backup_dir, f"{timestamp}.{fmt}")
    if fmt == "csv":
        with open(manifest_file, "w", newline="") as raw:
            writer = csv.writer(raw)
            writer.writerow(["filename", "hash", "user"])
            for (name, h) in manifest:
                writer.writerow([name, h, username])
    elif fmt == "json":
        records = [
            {"filename": name, "hash": h, "user": username}
            for (name, h) in manifest
        ]
        with open(manifest_file, "w") as raw:
            json.dump(records, raw, indent=2)
    else:
        raise ValueError(f"unknown format: {fmt}")


def copy_files(source_dir, backup_dir, manifest):
    for (filename, hash_code) in manifest:
        source_path = Path(source_dir, filename)
        backup_path = Path(backup_dir, f"{hash_code}.bck")
        if not backup_path.exists():
            shutil.copy(source_path, backup_path)


if __name__ == "__main__":
    fmt = "csv"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--json" in sys.argv:
        fmt = "json"
    assert len(args) == 2, "Usage: json_manifests.py source_dir backup_dir [--json]"
    backup(args[0], args[1], fmt)
