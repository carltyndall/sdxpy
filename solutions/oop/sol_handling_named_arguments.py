"""Solution: Handling Named Arguments exercise.

Extend `call` to capture and spread named arguments (`**kwargs`) so that
methods can accept keyword arguments in addition to positional ones.
"""

import math


# ----- shape infrastructure (from the chapter) -----

def call(thing, method_name, *args, **kwargs):
    """Call a method with both positional and named arguments."""
    method = find(thing["_class"], method_name)
    return method(thing, *args, **kwargs)


def find(cls, method_name):
    while cls is not None:
        if method_name in cls:
            return cls[method_name]
        cls = cls["_parent"]
    raise NotImplementedError(method_name)


def make(cls, *args):
    return cls["_new"](*args)


# ----- Shape base class -----

def shape_density(thing, weight):
    return weight / call(thing, "area")


def shape_new(name):
    return {
        "name": name,
        "_class": Shape
    }


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


def square_describe(thing, *, prefix="shape"):
    """A method that uses a keyword-only argument to label the square."""
    return f"{prefix}: square '{thing['name']}' (side={thing['side']})"


def square_larger(thing, size, *, scale=1.0):
    """Check if the square's area exceeds size * scale."""
    return call(thing, "area") > (size * scale)


def square_new(name, side):
    return make(Shape, name) | {
        "side": side,
        "_class": Square
    }


Square = {
    "perimeter": square_perimeter,
    "area": square_area,
    "describe": square_describe,
    "larger": square_larger,
    "_classname": "Square",
    "_parent": Shape,
    "_new": square_new
}


# ----- Circle -----

def circle_perimeter(thing):
    return 2 * math.pi * thing["radius"]


def circle_area(thing):
    return math.pi * thing["radius"] ** 2


def circle_describe(thing, *, prefix="shape"):
    return f"{prefix}: circle '{thing['name']}' (radius={thing['radius']})"


def circle_larger(thing, size, *, scale=1.0):
    return call(thing, "area") > (size * scale)


def circle_new(name, radius):
    return make(Shape, name) | {
        "radius": radius,
        "_class": Circle
    }


Circle = {
    "perimeter": circle_perimeter,
    "area": circle_area,
    "describe": circle_describe,
    "larger": circle_larger,
    "_classname": "Circle",
    "_parent": Shape,
    "_new": circle_new
}


# ----- demonstration -----

if __name__ == "__main__":
    sq = make(Square, "sq", 3)
    ci = make(Circle, "ci", 2)

    # Positional arguments still work.
    print(call(sq, "larger", 10))             # False

    # Named (keyword) arguments via **kwargs.
    print(call(sq, "larger", 10, scale=0.5))  # True

    # Keyword-only argument on describe.
    print(call(sq, "describe", prefix="item"))
    print(call(ci, "describe", prefix="item"))
