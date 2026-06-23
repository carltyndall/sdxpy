"""Solution: Multiple Inheritance exercise.

Extend the dictionary-based class system to support multiple inheritance
by replacing the single `_parent` reference with a `_parents` list.
The `find` function searches parents in left-to-right order using a
breadth-first approach that mimics Python's MRO more closely than a
naive depth-first search.
"""

import math


# ----- infrastructure -----

def call(thing, method_name, *args, **kwargs):
    method = find(thing["_class"], method_name)
    return method(thing, *args, **kwargs)


def find(cls, method_name):
    """Look up method_name in cls, then in each parent left to right.

    Uses a simple breadth-first traversal to approximate Python's C3
    linearization.  Each class keeps a `_parents` tuple; `find` visits
    the class first, then all parents in order, then grand-parents, and
    so on.
    """
    if method_name in cls:
        return cls[method_name]

    # Breadth-first queue of parent classes to visit.
    from collections import deque
    seen = {id(cls)}
    queue = deque(cls.get("_parents", ()))

    while queue:
        candidate = queue.popleft()
        if id(candidate) in seen:
            continue
        seen.add(id(candidate))
        if candidate is None:
            continue
        if method_name in candidate:
            return candidate[method_name]
        queue.extend(candidate.get("_parents", ()))

    raise NotImplementedError(method_name)


def make(cls, *args):
    return cls["_new"](*args)


# ----- base classes (mix-in style) -----

def shape_new(name):
    return {"name": name, "_class": Shape}


Shape = {
    "density": lambda thing, weight: weight / call(thing, "area"),
    "_classname": "Shape",
    "_parents": (),
    "_new": shape_new
}


def fillable_capacity(thing):
    """Return the fillable volume (area * depth) of a 2D shape."""
    return call(thing, "area") * thing.get("depth", 0)


Fillable = {
    "capacity": fillable_capacity,
    "_classname": "Fillable",
    "_parents": (),
    "_new": lambda name: {"name": name, "_class": Fillable}
}


def colored_hex(thing):
    return thing.get("color", "#000000")


Colored = {
    "hex": colored_hex,
    "_classname": "Colored",
    "_parents": (),
    "_new": lambda name: {"name": name, "_class": Colored}
}


# ----- Square: inherits from Shape and Colored -----

def square_perimeter(thing):
    return 4 * thing["side"]


def square_area(thing):
    return thing["side"] ** 2


def square_new(name, side, color="#ff0000"):
    return make(Shape, name) | {
        "side": side,
        "color": color,
        "_class": Square
    }


Square = {
    "perimeter": square_perimeter,
    "area": square_area,
    "_classname": "Square",
    "_parents": (Shape, Colored),
    "_new": square_new
}


# ----- Circle: inherits from Shape, Fillable, and Colored -----

def circle_perimeter(thing):
    return 2 * math.pi * thing["radius"]


def circle_area(thing):
    return math.pi * thing["radius"] ** 2


def circle_new(name, radius, depth=0, color="#00ff00"):
    return make(Shape, name) | {
        "radius": radius,
        "depth": depth,
        "color": color,
        "_class": Circle
    }


Circle = {
    "perimeter": circle_perimeter,
    "area": circle_area,
    "_classname": "Circle",
    "_parents": (Shape, Fillable, Colored),
    "_new": circle_new
}


# ----- demonstration -----

if __name__ == "__main__":
    sq = make(Square, "red-square", 3, color="#cc0000")
    ci = make(Circle, "deep-circle", 2, depth=5, color="#00cc00")

    # Methods from primary parent (Shape).
    print(f"{sq['name']} area: {call(sq, 'area')}")
    print(f"{ci['name']} perimeter: {call(ci, 'perimeter'):.2f}")

    # Methods from Colored mix-in.
    print(f"{sq['name']} color: {call(sq, 'hex')}")
    print(f"{ci['name']} color: {call(ci, 'hex')}")

    # Methods from Fillable mix-in (circle only).
    print(f"{ci['name']} capacity: {call(ci, 'capacity'):.2f}")

    # Shape.density is resolved through inheritance.
    print(f"{sq['name']} density (weight=10): {call(sq, 'density', 10):.2f}")
