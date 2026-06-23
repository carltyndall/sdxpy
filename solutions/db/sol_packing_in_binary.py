"""Solution for 'Packing in Binary' exercise.

1. Modify the experimental record class so that it packs itself in
   a fixed-size binary record using the ``struct`` module.
2. How does this change the file I/O operations in the database class?
3. Should those operations be moved into the record class or not?

The implementation below uses ``struct.pack`` and ``struct.unpack`` with
a format string that mirrors the original text layout: a fixed-length
name (encoded to UTF-8 and padded with null bytes), a signed 64-bit
timestamp, a byte count for the number of readings, and that many signed
32-bit reading values.

Binary packing means the database must open files in binary mode
(``"rb"`` / ``"wb"``) instead of text mode.  Moving the file I/O into
the record class would couple two responsibilities---serialisation and
persistence---that are cleaner to keep separate.
"""

import struct

from record_original import BasicRec


class Experiment(BasicRec):
    # Binary format: 6s q B 2i = 6 + 8 + 1 + 8 = 23 bytes (fixed)
    BINARY_FMT = f"<{BasicRec.MAX_NAME_LEN}sqB{BasicRec.MAX_READINGS_NUM}i"
    RECORD_LEN = struct.calcsize(BINARY_FMT)

    @staticmethod
    def size():
        return Experiment.RECORD_LEN

    @staticmethod
    def key(record):
        assert isinstance(record, Experiment)
        return record._name

    @staticmethod
    def pack(record):
        """Pack *record* into a fixed-size binary blob.

        The name is encoded as UTF-8 and padded/truncated to
        ``MAX_NAME_LEN`` bytes.  Readings shorter than the maximum are
        zero-filled.
        """
        assert isinstance(record, Experiment)
        name_bytes = record._name.encode("utf-8")[:BasicRec.MAX_NAME_LEN]
        readings = list(record._readings)
        # Pad readings with zeros up to MAX_READINGS_NUM.
        while len(readings) < BasicRec.MAX_READINGS_NUM:
            readings.append(0)
        return struct.pack(
            Experiment.BINARY_FMT,
            name_bytes,
            record._timestamp,
            len(record._readings),
            *readings[:BasicRec.MAX_READINGS_NUM],
        )

    @staticmethod
    def unpack(raw):
        """Unpack a fixed-size binary blob back into an ``Experiment``."""
        assert isinstance(raw, bytes) and len(raw) == Experiment.RECORD_LEN
        name_bytes, timestamp, num_readings, *readings = struct.unpack(
            Experiment.BINARY_FMT, raw
        )
        name = name_bytes.rstrip(b"\0").decode("utf-8")
        readings = [r for r in readings[:num_readings]]
        return Experiment(name, timestamp, readings)

    @staticmethod
    def pack_multi(records):
        return b"".join(Experiment.pack(r) for r in records)

    @staticmethod
    def unpack_multi(raw):
        size = Experiment.size()
        assert len(raw) % size == 0, "raw data is not a multiple of record size"
        count = len(raw) // size
        return [Experiment.unpack(raw[i * size:(i + 1) * size]) for i in range(count)]


if __name__ == "__main__":
    # Round-trip test.
    ex1 = Experiment("ex01", 12345, [1, 2])
    packed = Experiment.pack(ex1)
    assert isinstance(packed, bytes), "packed data must be bytes"
    assert len(packed) == Experiment.RECORD_LEN, "packed record is wrong size"
    unpacked = Experiment.unpack(packed)
    assert ex1 == unpacked, f"round-trip failed: {ex1} != {unpacked}"

    # Multi-record round-trip.
    ex2 = Experiment("ex02", 67890, [3, 4])
    multi_packed = Experiment.pack_multi([ex1, ex2])
    multi_unpacked = Experiment.unpack_multi(multi_packed)
    assert [ex1, ex2] == multi_unpacked, f"multi round-trip failed"

    print("All tests passed.")
    print()
    print("File I/O changes:")
    print("  - Must open files in binary mode ('rb' / 'wb')")
    print("  - Must use bytes instead of str for all read/write calls")
    print("  - No need for encode/decode at the file boundary")
    print()
    print("Should operations move into the record class?")
    print("  No.  Packing is about serialisation; file I/O is about")
    print("  persistence.  Keeping them separate means the database can")
    print("  swap storage backends (file, socket, cloud blob) without")
    print("  changing the record class, and the record class can evolve")
    print("  its binary layout without touching the storage layer.")
