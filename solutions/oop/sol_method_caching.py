"""Solution: Method Caching exercise.

Add a per-object method cache so that repeated calls to the same method
on the same object avoid walking the inheritance chain every time.  Each
object gets a `_cache` dictionary; `call` checks the cache before
delegating to `find`.
"""

import math


# ----- infrastructure with caching -----

def call(thing, method_name, *args, **kwargs):
    """Call a method, caching the resolved function on *thing*."""
    cache = thing.setdefault("_cache", {})
    method = cache.get(method_name)
    if method is None:
        method = find(thing["_class"], method_name)
        cache[method_name] = method
    return method(thing, *args, **kwargs)


def find(cls, method_name):
    """Iterative lookup: walk the _parent chain."""
    while cls is not None:
        if method_name in cls:
            return cls[method_name]
        cls = cls["_parent"]
    raise NotImplementedError(method_name)


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

    # First call: method is looked up and cached.
    print(call(sq, "area"))          # 9
    print(call(sq, "perimeter"))     # 12
    print(call(sq, "density", 10))   # ~1.11

    # The cache now contains the resolved functions.
    print("cache keys:", list(sq["_cache"].keys()))

    # Second call: method is retrieved from cache (no inheritance walk).
    print(call(sq, "area"))          # 9 (from cache)

    # Each object has its own cache.
    print(call(ci, "area"))          # ~12.57 (ci's own cache)
    print("sq cache:", list(sq["_cache"].keys()))
    print("ci cache:", list(ci["_cache"].keys()))
