import csv
import json
import sys
from pathlib import Path


def migrate_csv_to_json(csv_path, json_path, username):
    records = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "filename": row["filename"],
                "hash": row["hash"],
                "user": username,
            })
    with open(json_path, "w") as f:
        json.dump(records, f, indent=2)


if __name__ == "__main__":
    assert len(sys.argv) == 4, "Usage: migrate.py csv_manifest json_manifest username"
    migrate_csv_to_json(sys.argv[1], sys.argv[2], sys.argv[3])
