import csv
import shutil
import sys
from pathlib import Path


def sha256_hash(data):
    from hashlib import sha256
    return sha256(data).hexdigest()


def predictable_hash(data, length=8):
    text = data.decode("utf-8", errors="replace")
    return text[:length].ljust(length, "_")


MOCK_LEN = 8


def hash_all(root, hasher=sha256_hash, hash_len=None):
    from glob import glob
    if hash_len is None:
        hash_len = MOCK_LEN if hasher == predictable_hash else 16
    result = []
    for name in glob("**/*.*", root_dir=root, recursive=True):
        full_name = Path(root, name)
        with open(full_name, "rb") as reader:
            data = reader.read()
            hash_code = hasher(data)[:hash_len]
            result.append((name, hash_code))
    return result


def backup(source_dir, backup_dir, hasher=sha256_hash, hash_len=None):
    manifest = hash_all(source_dir, hasher=hasher, hash_len=hash_len)
    timestamp = current_time()
    write_manifest(backup_dir, timestamp, manifest)
    copy_files(source_dir, backup_dir, manifest)
    return manifest


def current_time():
    import time
    return f"{time.time()}".split(".")[0]


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
    assert len(sys.argv) == 3, "Usage: mock_hashes.py source_dir backup_dir"
    backup(sys.argv[1], sys.argv[2])
