"""Demonstrate the actual probability of hash collision with 2-bit hashes."""


def collision_probability(num_bits, num_files):
    """Probability of at least one collision with num_bits hash and num_files."""
    num_buckets = 2 ** num_bits
    prob_no_collision = 1.0
    for i in range(num_files):
        prob_no_collision *= (num_buckets - i) / num_buckets
    return 1.0 - prob_no_collision


if __name__ == "__main__":
    bits = 2
    buckets = 2 ** bits
    print(f"With {bits}-bit hashes, there are {buckets} possible hash values.\n")

    for n in range(1, 6):
        p = collision_probability(bits, n)
        print(f"After {n} file(s): probability of at least one collision = {p:.4f} ({p*100:.1f}%)")

    print()
    print("With 4 files, the actual odds of a collision are about 90.6%, not 75%.")
