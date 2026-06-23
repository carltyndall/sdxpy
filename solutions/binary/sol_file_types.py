"""Solution for 'File Types' exercise.

Determine whether a file is a PNG image by inspecting its first eight
bytes.  PNG files always begin with the magic bytes:

    137 80 78 71 13 10 26 10

(The four bytes 80 78 71 13 spell 'PNG' in ASCII.)
"""

PNG_SIGNATURE = bytes([137, 80, 78, 71, 13, 10, 26, 10])


def is_png(filepath):
    """Return True if *filepath* starts with the PNG magic bytes."""
    with open(filepath, "rb") as f:
        header = f.read(len(PNG_SIGNATURE))
    return header == PNG_SIGNATURE


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: sol_file_types.py <filename>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if is_png(path):
        print(f"{path} is a PNG image.")
    else:
        print(f"{path} is NOT a PNG image.")
