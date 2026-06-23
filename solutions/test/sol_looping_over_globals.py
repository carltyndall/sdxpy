"""Solution: Looping Over globals.

The first snippet raises RuntimeError because the for-loop variable 'name'
is added to the globals dictionary while we are iterating over it.
Python detects the size change and stops.

The second snippet works because 'name' already exists in globals before
the loop: reassigning an existing key does not change the dictionary size.
"""

print("=== First snippet: this will fail ===")
try:
    for name in globals():
        print(name)
except RuntimeError as exc:
    print(f"RuntimeError: {exc}")

print()
print("=== Second snippet: this will work ===")
name = None
for name in globals():
    print(name)
