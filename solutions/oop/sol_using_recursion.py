"""Solution: Using Recursion exercise.

Replace the iterative `find` with a recursive version that calls itself
to walk up the `_parent` chain.  The two versions are compared at the
end.

The recursive version is arguably easier to read---there is no mutable
state and the base case is explicit---but Python's recursion limit and
function-call overhead make the iterative version safer for deep
inheritance chains and slightly faster on most CPython versions.
"""

import math


# ----- infrastructure with recursive find -----

def call(thing, method_name, *args, **kwargs):
    method = find(thing["_class"], method_name)
    return method(thing, *args, **kwargs)


def find(cls, method_name):
    """Recursively search for *method_name* in *cls* and its ancestors."""
    if cls is None:
        raise NotImplementedError(method_name)
    if method_name in cls:
        return cls[method_name]
    return find(cls.get("_parent"), method_name)


def make(cls, *args):
    return cls["_new"](*args)


# ----- Shape -----

def shape_density(thing, weight):
    return weight / call(thing, "area")


def shape_new(name):
    return {"name": name, "_class": Shape}


Shape = {
    "density": shape_density,
    "_classname": "Shape",
    "_parent": None,
    "_new": shape_new
}


# ----- Square -----

def square_perimeter(thing):
    return 4 * thing["side"]


def square_area(thing):
    return thing["side"] ** 2


def square_new(name, side):
    return make(Shape, name) | {
        "side": side,
        "_class": Square
    }


Square = {
    "perimeter": square_perimeter,
    "area": square_area,
    "_classname": "Square",
    "_parent": Shape,
    "_new": square_new
}


# ----- Circle -----

def circle_perimeter(thing):
    return 2 * math.pi * thing["radius"]


def circle_area(thing):
    return math.pi * thing["radius"] ** 2


def circle_new(name, radius):
    return make(Shape, name) | {
        "radius": radius,
        "_class": Circle
    }


Circle = {
    "perimeter": circle_perimeter,
    "area": circle_area,
    "_classname": "Circle",
    "_parent": Shape,
    "_new": circle_new
}


# ----- demonstration -----

if __name__ == "__main__":
    sq = make(Square, "sq", 3)
    ci = make(Circle, "ci", 2)

    # Methods defined directly on the class still work.
    print(call(sq, "area"))       # 9
    print(call(ci, "perimeter"))  # ~12.57

    # Inherited methods are found via recursive find.
    d_sq = call(sq, "density", 10)
    d_ci = call(ci, "density", 10)
    print(f"{sq['name']}: {d_sq:.2f}")
    print(f"{ci['name']}: {d_ci:.2f}")

    # A missing method still raises NotImplementedError.
    try:
        call(sq, "nonexistent")
    except NotImplementedError as exc:
        print(f"Correctly raised: {exc}")
