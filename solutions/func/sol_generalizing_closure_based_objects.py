"""Demonstrate generalized closure-based objects with arbitrary named fields."""


def make_object(**kwargs):
    """Create an object with getter and setter for any named fields."""
    private = dict(kwargs)

    def getter(name):
        return private[name]

    def setter(name, value):
        private[name] = value

    return {"get": getter, "set": setter}


# Create an object with multiple fields.
point = make_object(x=0, y=0, label="origin")
print("initial x:", point["get"]("x"))
print("initial label:", point["get"]("label"))

# Update a field.
point["set"]("x", 10)
point["set"]("y", 20)
print("after update, x:", point["get"]("x"))
print("after update, y:", point["get"]("y"))

# Add a new field on the fly.
point["set"]("color", "red")
print("new field 'color':", point["get"]("color"))

# Getting a missing key raises KeyError.
try:
    point["get"]("nonexistent")
except KeyError as e:
    print(f"missing key raises {type(e).__name__}: {e}")

# The setter accepts any type for a new or existing key.
point["set"]("x", "now a string")
print("x after type change:", point["get"]("x"))
