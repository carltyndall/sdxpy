"""Solution for 'Implement Compaction' exercise.

Add a static method to the database that compacts blocks, i.e., rewrites
all of the blocks so that only live records are stored and stale (dead)
records are removed.  This reduces disk usage and improves scan
performance.

The approach: walk every block, collect only the records whose keys
appear in the index with a matching sequence id (meaning they are the
most recent version), then repack and rewrite each block.  After
compaction some blocks may shrink, so we also remove any now-empty
trailing blocks.
"""

import tempfile
from pathlib import Path

from record_original import BasicRec
from cleanup import Cleanup


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


class Compacted(Cleanup):
    """A log-structured database that compacts blocks on command."""

    @staticmethod
    def compact(db):
        """Rewrite every block so that it contains only live records.

        A record is *live* when its key appears in the index and the
        index maps that key to the record's sequence id.  Dead records
        (older versions of an overwritten key) are dropped.
        """
        # Build a set of live sequence ids.
        live_seq = set(db._index.values())

        new_blocks = []
        for block in db._blocks:
            # Keep only records whose sequence id is live.
            live = {seq: rec for seq, rec in block.items() if seq in live_seq}
            new_blocks.append(live)

        # Drop empty trailing blocks.
        while new_blocks and not new_blocks[-1]:
            new_blocks.pop()

        # Rebuild the index with new sequence ids.
        db._blocks = new_blocks
        new_index = {}
        next_seq = 0
        for block in db._blocks:
            for seq_id in sorted(block):
                rec = block[seq_id]
                key = db._record_cls.key(rec)
                new_index[key] = next_seq
                next_seq += 1
        db._index = new_index
        db._next = next_seq

        # Write blocks back to disk.
        last_written = -1
        for block_id, block in enumerate(db._blocks):
            packed = db._record_cls.pack_multi(block.values())
            filename = db._get_filename(block_id)
            with open(filename, "w") as writer:
                writer.write(packed)
            last_written = block_id

        # Remove any leftover block files beyond the current count.
        existing = sorted(db._db_dir.iterdir())
        for filename in existing[last_written + 1:]:
            Path(filename).unlink()


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Compacted(Experiment, tmpdir)

        # Add some records.
        db.add(Experiment("a", 1, [10]))
        db.add(Experiment("b", 2, [20]))
        db.add(Experiment("c", 3, [30]))

        # Overwrite 'b' to create a stale record.
        db.add(Experiment("b", 99, [99]))

        # Before compaction 'b' has the latest value.
        assert db.get("b")._timestamp == 99
        initial_blocks = db.num_blocks()

        # Compact.
        Compacted.compact(db)

        # After compaction the stale 'b' is gone, live records remain.
        assert db.get("a") is not None
        assert db.get("b")._timestamp == 99
        assert db.get("c") is not None

        # Blocks should never increase after compaction.
        assert db.num_blocks() <= initial_blocks

        print("All tests passed.")
        print(f"Blocks before compaction: {initial_blocks}")
        print(f"Blocks after compaction:  {db.num_blocks()}")
