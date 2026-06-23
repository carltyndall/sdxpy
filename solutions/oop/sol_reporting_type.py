"""Solution: Reporting Type exercise.

Add `type_of` and `is_instance_of` functions that mimic Python's
built-in `type` and `isinstance` for the dictionary-based object system.

- `type_of(thing)` returns the class dictionary of the most-specific
  type (the value of `thing["_class"]`).
- `is_instance_of(thing, cls)` walks the inheritance chain (via
  `_parent`) and returns True if `thing`'s class is `cls` or inherits
  from `cls` at any level.
"""

import math


# ----- infrastructure -----

def call(thing, method_name, *args, **kwargs):
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


def type_of(thing):
    """Return the most-specific class dictionary for *thing*."""
    return thing["_class"]


def is_instance_of(thing, cls):
    """Return True if *thing*'s class is *cls* or inherits from it."""
    candidate = thing["_class"]
    while candidate is not None:
        if candidate is cls:
            return True
        candidate = candidate.get("_parent")
    return False


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

    # type_of returns the most specific class.
    print(type_of(sq) is Square)   # True
    print(type_of(ci) is Circle)   # True
    print(type_of(sq) is Shape)    # False (most-specific is Square)

    # is_instance_of checks the whole inheritance chain.
    print(is_instance_of(sq, Square))   # True
    print(is_instance_of(sq, Shape))    # True (Square inherits Shape)
    print(is_instance_of(sq, Circle))   # False
    print(is_instance_of(ci, Shape))    # True (Circle inherits Shape)
    print(is_instance_of(ci, Square))   # False
