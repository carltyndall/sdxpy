import csv
import importlib.util
import shutil
import sys
import time
from pathlib import Path

from hash_all import hash_all


def load_pre_commit(source_dir):
    hook_path = Path(source_dir, "pre_commit.py")
    if not hook_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(
        "pre_commit_hook", str(hook_path)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "pre_commit", None)


def backup(source_dir, backup_dir):
    pre_commit = load_pre_commit(source_dir)
    if pre_commit is not None:
        try:
            if not pre_commit(source_dir):
                print("pre_commit hook returned False, aborting backup",
                      file=sys.stderr)
                return None
        except Exception as e:
            print(f"pre_commit hook raised {type(e).__name__}: {e}",
                  file=sys.stderr)
            return None

    manifest = hash_all(source_dir)
    timestamp = f"{time.time()}".split(".")[0]
    write_manifest(backup_dir, timestamp, manifest)
    copy_files(source_dir, backup_dir, manifest)
    return manifest


def write_manifest(backup_dir, timestamp, manifest):
    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    manifest_file = Path(backup_dir, f"{timestamp}.csv")
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
    assert len(sys.argv) == 3, (
        "Usage: pre_commit_hooks.py source_dir backup_dir"
    )
    backup(sys.argv[1], sys.argv[2])
