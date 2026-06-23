"""Solution for 'Packing Null Bytes' exercise.

Modify the experimental record class so that records are packed as strings
but can safely contain null bytes.  Instead of using null bytes as field
separators, we prefix each field with its decimal length followed by a
colon, then concatenate the fields.  A trailing newline marks the end of
the record so that multi-record packing still works cleanly.
"""

from record_original import BasicRec


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
        """Pack *record* into a length-prefixed string.

        Each field is written as ``len:value`` and fields are joined
        without a separator.  A trailing newline terminates the record
        so that ``pack_multi`` can split on newlines without ambiguity.
        This encoding can represent any string value, including strings
        that contain null bytes or colons.
        """
        assert isinstance(record, Experiment)
        fields = [
            record._name,
            str(record._timestamp),
            ",".join(str(r) for r in record._readings),
        ]
        parts = [f"{len(f)}:{f}" for f in fields]
        return "".join(parts) + "\n"

    @staticmethod
    def unpack(raw):
        """Unpack a length-prefixed string back into an ``Experiment``.

        The trailing newline is stripped; then we read each ``len:value``
        piece in order: name, timestamp, and the comma-separated readings.
        """
        assert isinstance(raw, str)
        raw = raw.rstrip("\n")
        pos = 0
        values = []
        while pos < len(raw):
            colon = raw.index(":", pos)
            length = int(raw[pos:colon])
            pos = colon + 1
            values.append(raw[pos:pos + length])
            pos += length
        name, timestamp_str, readings_str = values
        timestamp = int(timestamp_str)
        readings = [int(r) for r in readings_str.split(",")] if readings_str else []
        return Experiment(name, timestamp, readings)

    @staticmethod
    def pack_multi(records):
        return "".join(Experiment.pack(r) for r in records)

    @staticmethod
    def unpack_multi(raw):
        lines = raw.split("\n")
        # The final empty string after the last newline is not a record.
        if lines and lines[-1] == "":
            lines.pop()
        return [Experiment.unpack(line + "\n") for line in lines]


if __name__ == "__main__":
    # Test round-trip with ordinary data.
    ex1 = Experiment("ex01", 12345, [1, 2])
    packed = Experiment.pack(ex1)
    unpacked = Experiment.unpack(packed)
    assert ex1 == unpacked, f"round-trip failed: {ex1} != {unpacked}"

    # Test a name that contains a null byte (simulated via chr(0)).
    ex2 = Experiment("a\0b", 99999, [])
    packed2 = Experiment.pack(ex2)
    unpacked2 = Experiment.unpack(packed2)
    assert ex2 == unpacked2, f"null-byte round-trip failed: {ex2._name!r} != {unpacked2._name!r}"

    # Test multi-record round-trip.
    records = [ex1, ex2]
    packed_multi = Experiment.pack_multi(records)
    unpacked_multi = Experiment.unpack_multi(packed_multi)
    assert records == unpacked_multi, f"multi round-trip failed: {records} != {unpacked_multi}"

    print("All tests passed.")
