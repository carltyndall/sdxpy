"""Plot SHA-256 hash codes for unique lines of a text file to check distribution."""

import sys
from collections import Counter
from hashlib import sha256

try:
    import plotly.express as px
    import plotly.io as pio
except ImportError:
    print("This script requires plotly. Install with: pip install plotly")
    sys.exit(1)

pio.kaleido.scope.mathjax = None


def hash_line(line):
    """Return integer SHA-256 hash of a line."""
    digest = sha256(line).hexdigest()
    return int(digest, 16)


def plot_histogram(values, stem, num_bins=20):
    """Plot a histogram of integer values and save to SVG and PDF."""
    fig = px.histogram(
        {"hash": values}, x="hash", nbins=num_bins,
        color_discrete_sequence=["gray"],
        template="plotly_white"
    )
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
    fig.write_image(f"{stem}.svg", height=300)
    fig.write_image(f"{stem}.pdf", height=300)
    print(f"Saved histogram to {stem}.svg and {stem}.pdf")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sol_how-good-is-sha-256.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r") as f:
        lines = [ln.strip().encode("utf-8") for ln in f.readlines() if ln.strip()]

    unique = list(set(lines))
    print(f"Total non-blank lines: {len(lines)}, unique lines: {len(unique)}")

    hashes = [hash_line(ln) for ln in unique]
    print(f"Hash range: {min(hashes)} to {max(hashes)}")

    # Check that all hashes are unique (as expected with SHA-256)
    counts = Counter(hashes)
    print(f"All hashes unique: {len(counts) == len(unique)}")

    stem = filename.rsplit(".", 1)[0]
    plot_histogram(hashes, f"{stem}_sha256_histogram")
