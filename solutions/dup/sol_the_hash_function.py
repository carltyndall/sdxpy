"""Demonstrate Python's built-in hash function and why mutable types are unhashable."""


if __name__ == "__main__":
    print("hash(123):", hash(123))
    print("hash('123'):", hash("123"))
    print()
    print("Both work because integers and strings are immutable (hashable).")
    print()
    print("Trying hash([123]) would raise:")
    print("  TypeError: unhashable type: 'list'")
    print()
    print("Lists are mutable, so Python refuses to hash them.")
    print("If a list's hash were allowed and the list changed later,")
    print("dictionary lookups would break because the stored hash")
    print("would no longer match the modified object.")

    # Demonstrate that it indeed raises
    try:
        hash([123])
    except TypeError as e:
        print(f"\nConfirmed: {e}")
