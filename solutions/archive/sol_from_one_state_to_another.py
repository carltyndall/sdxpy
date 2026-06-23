import csv
import shutil
import sys
from pathlib import Path

from hash_all import hash_all


def from_to(target_dir, backup_dir, manifest_path):
    target_dir = Path(target_dir)
    backup_dir = Path(backup_dir)

    with open(manifest_path, "r") as f:
        reader = csv.DictReader(f)
        manifest = {row["filename"]: row["hash"] for row in reader}

    current = dict(hash_all(str(target_dir)))

    for name, want_hash in manifest.items():
        target_path = Path(target_dir, name)
        have_hash = current.get(name)
        if have_hash == want_hash:
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path = Path(backup_dir, f"{want_hash}.bck")
        shutil.copy(source_path, target_path)

    for name in current:
        if name not in manifest:
            target_path = Path(target_dir, name)
            target_path.unlink()
            try:
                target_path.parent.rmdir()
            except OSError:
                pass


if __name__ == "__main__":
    assert len(sys.argv) == 4, (
        "Usage: from_to.py target_dir backup_dir manifest.csv"
    )
    from_to(sys.argv[1], sys.argv[2], sys.argv[3])
