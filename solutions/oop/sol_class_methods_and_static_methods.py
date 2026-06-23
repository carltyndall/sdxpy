"""Solution: Class Methods and Static Methods exercise.

Demonstrate the difference between instance methods, class methods, and
static methods using the dictionary-based object system.

- An *instance method* receives the object (thing) as its first argument.
- A *class method* receives the class dictionary as its first argument;
  we signal this by prefixing the function name with `class_` and having
  `call` pass `thing["_class"]` instead of `thing`.
- A *static method* receives neither the object nor the class;
  `call` simply invokes the function with the extra arguments.
"""

import math


# ----- infrastructure (extended) -----

def call(thing, method_name, *args, **kwargs):
    """Dispatch a method call, adapting the first argument by convention."""
    method = find(thing["_class"], method_name)
    return method(thing, *args, **kwargs)


def call_class(cls, method_name, *args, **kwargs):
    """Call a class method, passing the class dict as the first argument."""
    method = find(cls, method_name)
    return method(cls, *args, **kwargs)


def find(cls, method_name):
    while cls is not None:
        if method_name in cls:
            return cls[method_name]
        cls = cls["_parent"]
    raise NotImplementedError(method_name)


def make(cls, *args):
    return cls["_new"](*args)


# ----- Shape base -----

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


# ----- Square with a class method and a static method -----

def square_perimeter(thing):
    return 4 * thing["side"]


def square_area(thing):
    return thing["side"] ** 2


# ---- class method ----
def square_classname(cls):
    """Return the human-readable class name stored on the class dict."""
    return cls.get("_classname", "unknown")


# ---- static method ----
def square_unit():
    """Return the unit used when measuring squares in this system.

    A static method: it needs no object or class state to do its job.
    """
    return "square metres"


def square_new(name, side):
    return make(Shape, name) | {
        "side": side,
        "_class": Square
    }


Square = {
    "perimeter": square_perimeter,
    "area": square_area,
    "classname": square_classname,
    "unit": square_unit,
    "_classname": "Square",
    "_parent": Shape,
    "_new": square_new
}


# ----- Circle -----

def circle_perimeter(thing):
    return 2 * math.pi * thing["radius"]


def circle_area(thing):
    return math.pi * thing["radius"] ** 2


def circle_classname(cls):
    return cls.get("_classname", "unknown")


def circle_unit():
    return "square metres"


def circle_new(name, radius):
    return make(Shape, name) | {
        "radius": radius,
        "_class": Circle
    }


Circle = {
    "perimeter": circle_perimeter,
    "area": circle_area,
    "classname": circle_classname,
    "unit": circle_unit,
    "_classname": "Circle",
    "_parent": Shape,
    "_new": circle_new
}


# ----- demonstration -----

if __name__ == "__main__":
    sq = make(Square, "sq", 3)
    ci = make(Circle, "ci", 2)

    # Instance methods: called on an object.
    print(call(sq, "area"))                 # 9
    print(call(ci, "perimeter"))            # ~12.57

    # Class methods: called on the class dictionary directly.
    print(call_class(Square, "classname"))  # "Square"
    print(call_class(Circle, "classname"))  # "Circle"

    # Static methods: call_class works because the method simply ignores
    # the first argument, but conceptually no object/class is needed.
    print(call_class(Square, "unit"))       # "square metres"
    print(call_class(Circle, "unit"))       # "square metres"

    # You can also obtain the function from the class dict and call it
    # with no arguments, which is the cleanest approximation of a static
    # method in this dictionary-based system.
    print(Square["unit"]())                 # "square metres"
