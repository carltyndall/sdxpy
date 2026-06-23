"""Solution for 'Save the Index Separately' exercise.

1. Modify the database so that it saves the entire index in a single
   file alongside the block files.
2. Design and run an experiment to determine if this change improves
   performance or not.

The idea: instead of reconstructing the index by scanning every block
file at startup, we cache the index in a dedicated ``index.dat`` file
using JSON.  On restart we load the index from that file, which is an
O(1)-disk-read operation instead of O(num_blocks).

The experiment script at the bottom compares startup time with and
without the separate index file.  For large databases with many blocks
the separate index is a clear win; for small databases the difference
may be lost in system noise.
"""

import json
import tempfile
import time
from pathlib import Path

from record_original import BasicRec
from blocked_file import BlockedFile


class Experiment(BasicRec):
    RECORD_LEN = BasicRec.MAX_NAME_LEN + 1 \
        + BasicRec.TIMESTAMP_LEN + 1 \
        + (BasicRec.MAX_READING_LEN * BasicRec.MAX_READINGS_NUM) \
        + (BasicRec.MAX_READINGS_NUM - 1)

    @staticmethod
    def size():
        return Experiment.RECORD_LEN

    @staticmethod
    def key(record):
        assert isinstance(record, Experiment)
        return record._name

    @staticmethod
    def pack(record):
        assert isinstance(record, Experiment)
        readings = "\0".join(str(r) for r in record._readings)
        result = f"{record._name}\0{record._timestamp}\0{readings}"
        if len(result) < Experiment.RECORD_LEN:
            result += "\0" * (Experiment.RECORD_LEN - len(result))
        return result

    @staticmethod
    def unpack(raw):
        assert isinstance(raw, str)
        parts = raw.split("\0")
        name = parts[0]
        timestamp = int(parts[1])
        readings = [int(r) for r in parts[2:] if len(r)]
        return Experiment(name, timestamp, readings)

    @staticmethod
    def pack_multi(records):
        return "".join(Experiment.pack(r) for r in records)

    @staticmethod
    def unpack_multi(raw):
        size = Experiment.size()
        split = [raw[i:i + size] for i in range(0, len(raw), size)]
        return [Experiment.unpack(s) for s in split]


class IndexedFile(BlockedFile):
    """BlockedFile that persists the index in a separate ``index.dat``."""

    INDEX_FILENAME = "index.dat"

    def __init__(self, record_cls, db_dir):
        # Skip BlockedFile.__init__ so we can replace _build_index.
        super(BlockedFile, self).__init__(record_cls)
        self._db_dir = Path(db_dir)
        self._db_dir.mkdir(parents=True, exist_ok=True)
        index_path = self._db_dir / self.INDEX_FILENAME
        if index_path.exists():
            self._load_index()
        else:
            self._build_index()

    def add(self, record):
        super(BlockedFile, self).add(record)
        self._save(record)
        self._save_index()

    def _save_index(self):
        """Write the current index to ``index.dat`` as JSON."""
        index_path = self._db_dir / self.INDEX_FILENAME
        with open(index_path, "w") as writer:
            json.dump({"index": self._index, "next": self._next}, writer)

    def _load_index(self):
        """Restore the index from ``index.dat``."""
        index_path = self._db_dir / self.INDEX_FILENAME
        with open(index_path, "r") as reader:
            data = json.load(reader)
        self._index = data["index"]
        self._next = data["next"]


# ---------------------------------------------------------------------------
# Performance experiment
# ---------------------------------------------------------------------------

def build_database(cls, db_dir, num_records):
    """Create a database of *num_records* using *cls* and return it."""
    db = cls(Experiment, db_dir)
    for i in range(num_records):
        db.add(Experiment(f"rec{i:04d}", 1000 + i, [i % 10, (i + 1) % 10]))
    return db


def time_restart(cls, db_dir):
    """Return seconds to construct a fresh instance of *cls* on an
    existing *db_dir*."""
    start = time.perf_counter()
    _ = cls(Experiment, db_dir)
    return time.perf_counter() - start


if __name__ == "__main__":
    NUM_RECORDS = 100
    WARMUP_RUNS = 3
    MEASURED_RUNS = 10

    with tempfile.TemporaryDirectory() as tmpdir:
        # One directory for the baseline, one for the indexed variant.
        base_dir = Path(tmpdir) / "base"
        index_dir = Path(tmpdir) / "indexed"

        # Build identical databases.
        build_database(BlockedFile, base_dir, NUM_RECORDS)
        build_database(IndexedFile, index_dir, NUM_RECORDS)

        # Warm up.
        for _ in range(WARMUP_RUNS):
            time_restart(BlockedFile, base_dir)
            time_restart(IndexedFile, index_dir)

        # Measure.
        base_times = []
        index_times = []
        for _ in range(MEASURED_RUNS):
            base_times.append(time_restart(BlockedFile, base_dir))
            index_times.append(time_restart(IndexedFile, index_dir))

        avg_base = sum(base_times) / len(base_times)
        avg_index = sum(index_times) / len(index_times)

        print(f"Records: {NUM_RECORDS}")
        print(f"Baseline (no index file): {avg_base * 1000:.3f} ms")
        print(f"Indexed  (index.dat):      {avg_index * 1000:.3f} ms")
        speedup = avg_base / avg_index if avg_index > 0 else float("inf")
        print(f"Speedup: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")

        # Sanity check: data should be identical.
        base_db = BlockedFile(Experiment, base_dir)
        index_db = IndexedFile(Experiment, index_dir)
        for i in range(NUM_RECORDS):
            key = f"rec{i:04d}"
            assert base_db.get(key) == index_db.get(key), f"mismatch at {key}"
        print("Data integrity check passed.")
