import csv
import sys
from pathlib import Path


def read_manifest(path):
    records = {}
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records[row["filename"]] = row["hash"]
    return records


def file_history(backup_dir, filename):
    backup_dir = Path(backup_dir)
    manifests = sorted(
        [p for p in backup_dir.iterdir() if p.suffix == ".csv"],
        key=lambda p: p.name,
    )

    history = []
    last_hash = None

    for m_path in manifests:
        records = read_manifest(m_path)
        if filename not in records:
            continue
        current_hash = records[filename]
        if current_hash != last_hash:
            timestamp = m_path.stem
            history.append((timestamp, current_hash))
            last_hash = current_hash

    return history


def report(filename, history):
    if not history:
        print(f"No history found for {filename}")
        return
    print(f"History of {filename}:")
    for timestamp, h in history:
        print(f"    {timestamp}: {h}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: file_history.py backup_dir filename"
    history = file_history(sys.argv[1], sys.argv[2])
    report(sys.argv[2], history)
