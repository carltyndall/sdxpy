"""Demonstrate O(N^2) growth of pairwise connections in a system."""


def pairwise_count(n):
    """Number of unique pairs among N items."""
    return n * (n - 1) // 2


if __name__ == "__main__":
    sizes = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    print("Components (N) | Unique Pairs N(N-1)/2 | Ratio to previous")
    print("-" * 60)
    prev = None
    for n in sizes:
        pairs = pairwise_count(n)
        ratio = f"{pairs / prev:.1f}x" if prev else "-"
        print(f"  {n:>10}   | {pairs:>22}   | {ratio}")
        prev = pairs

    print()
    print("Each time N doubles, the number of pairs roughly quadruples.")
    print("This is the hallmark of O(N^2) growth.")
