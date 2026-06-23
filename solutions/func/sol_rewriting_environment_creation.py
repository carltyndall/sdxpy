"""Demonstrate rewriting the zip/dict line with an explicit loop."""

# Simulated interpreter values.
params = ["num", "scale"]
values = [7, 3]

# Original one-liner.
original = dict(zip(params, values))
print("original:", original)

# Rewritten with an explicit loop.
frame = {}
for param, value in zip(params, values):
    frame[param] = value
print("rewritten:", frame)

# Verify they produce the same result.
assert original == frame
print("Both approaches produce the same dictionary.")
