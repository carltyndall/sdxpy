"""Solution for 'Encoding and Decoding' exercise.

Manually encode a list of Unicode code points into UTF-8 bytes and
decode a list of UTF-8 bytes back into code points.

UTF-8 splits code points into the following ranges:

- 0x00 – 0x7F       → 1 byte:  0xxxxxxx
- 0x80 – 0x7FF      → 2 bytes: 110xxxxx 10xxxxxx
- 0x800 – 0xFFFF    → 3 bytes: 1110xxxx 10xxxxxx 10xxxxxx
- 0x10000 – 0x10FFFF → 4 bytes: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx

Every continuation byte must begin with the bits ``10``.
"""


def encode_utf8(code_points):
    """Return a list of byte-sized integers representing the UTF-8
    encoding of *code_points*.
    """
    result = []
    for cp in code_points:
        if cp < 0x80:
            result.append(cp)
        elif cp < 0x800:
            result.append(0xC0 | (cp >> 6))
            result.append(0x80 | (cp & 0x3F))
        elif cp < 0x10000:
            result.append(0xE0 | (cp >> 12))
            result.append(0x80 | ((cp >> 6) & 0x3F))
            result.append(0x80 | (cp & 0x3F))
        elif cp < 0x110000:
            result.append(0xF0 | (cp >> 18))
            result.append(0x80 | ((cp >> 12) & 0x3F))
            result.append(0x80 | ((cp >> 6) & 0x3F))
            result.append(0x80 | (cp & 0x3F))
        else:
            raise ValueError(f"code point {cp:#x} out of Unicode range")
    return result


def decode_utf8(bytes_list):
    """Decode a list of UTF-8 byte values into a list of code points.

    Raises ``ValueError`` if the byte sequence is malformed.
    """
    code_points = []
    i = 0
    n = len(bytes_list)

    while i < n:
        b0 = bytes_list[i]

        # Determine byte count from the leading bits.
        if (b0 & 0x80) == 0:
            byte_count = 1
        elif (b0 & 0xE0) == 0xC0:
            byte_count = 2
        elif (b0 & 0xF0) == 0xE0:
            byte_count = 3
        elif (b0 & 0xF8) == 0xF0:
            byte_count = 4
        else:
            # Continuation byte (10xxxxxx) appearing where a lead byte
            # was expected.
            raise ValueError(
                f"unexpected byte {b0:#04x} at position {i}"
            )

        if i + byte_count > n:
            raise ValueError(
                f"truncated sequence: need {byte_count} bytes "
                f"but only {n - i} remain at position {i}"
            )

        # Extract the payload bits from the first byte.
        if byte_count == 1:
            cp = b0
        elif byte_count == 2:
            cp = b0 & 0x1F
        elif byte_count == 3:
            cp = b0 & 0x0F
        else:
            cp = b0 & 0x07

        # Verify and extract continuation bytes.
        for j in range(1, byte_count):
            bj = bytes_list[i + j]
            if (bj & 0xC0) != 0x80:
                raise ValueError(
                    f"expected continuation byte at position {i + j}, "
                    f"got {bj:#04x}"
                )
            cp = (cp << 6) | (bj & 0x3F)

        code_points.append(cp)
        i += byte_count

    return code_points


if __name__ == "__main__":
    # Round-trip: every code point in the BMP and a few above.
    test_points = list(range(0x80)) + [0xA3, 0x3A9, 0x4E16, 0x1F600]
    encoded = encode_utf8(test_points)
    decoded = decode_utf8(encoded)
    assert decoded == test_points, f"round-trip failed: {decoded[:10]}"

    # Verify against Python's built-in UTF-8.
    text = "".join(chr(cp) for cp in test_points)
    expected = list(text.encode("utf-8"))
    assert encoded == expected, "encoding disagrees with Python"

    # Malformed: stray continuation byte.
    try:
        decode_utf8([0x80])
    except ValueError as e:
        print(f"Correctly caught: {e}")

    # Malformed: truncated multi-byte sequence.
    try:
        decode_utf8([0xC2])
    except ValueError as e:
        print(f"Correctly caught: {e}")

    print("All tests passed.")
