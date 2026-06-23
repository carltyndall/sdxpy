"""Solution: fixed-size one-dimensional arrays.

Adds three operations:
- ["array", size]  creates a list of <size> None values
- ["aget", arr, idx]  gets element at <idx> from <arr>
- ["aset", arr, idx, val]  sets element at <idx> to <val>
"""

import json
import sys


def do_abs(env, args):
    assert len(args) == 1
    val = do(env, args[0])
    return abs(val)


def do_add(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    return left + right


def do_aget(env, args):
    """Get an array element by index: ["aget", arr_expr, idx_expr]."""
    assert len(args) == 2
    arr = do(env, args[0])
    idx = do(env, args[1])
    assert isinstance(arr, list), f"aget: expected a list, got {type(arr)}"
    assert isinstance(idx, int), f"aget: index must be an integer, got {type(idx)}"
    assert 0 <= idx < len(arr), f"aget: index {idx} out of range (len={len(arr)})"
    return arr[idx]


def do_array(env, args):
    """Create a fixed-size array: ["array", size]."""
    assert len(args) == 1
    size = do(env, args[0])
    assert isinstance(size, int) and size >= 0, f"array: size must be a non-negative integer"
    return [None] * size


def do_aset(env, args):
    """Set an array element by index: ["aset", arr_expr, idx_expr, val_expr]."""
    assert len(args) == 3
    arr = do(env, args[0])
    idx = do(env, args[1])
    val = do(env, args[2])
    assert isinstance(arr, list), f"aset: expected a list, got {type(arr)}"
    assert isinstance(idx, int), f"aset: index must be an integer, got {type(idx)}"
    assert 0 <= idx < len(arr), f"aset: index {idx} out of range (len={len(arr)})"
    arr[idx] = val
    return val


def do_get(env, args):
    assert len(args) == 1
    assert isinstance(args[0], str)
    assert args[0] in env, f"Unknown variable {args[0]}"
    return env[args[0]]


def do_print(env, args):
    values = [do(env, a) for a in args]
    print(*values)
    return None


def do_seq(env, args):
    for item in args:
        result = do(env, item)
    return result


def do_set(env, args):
    assert len(args) == 2
    assert isinstance(args[0], str)
    value = do(env, args[1])
    env[args[0]] = value
    return value


OPS = {
    name.replace("do_", ""): func
    for (name, func) in globals().items()
    if name.startswith("do_")
}


def do(env, expr):
    if isinstance(expr, int):
        return expr
    assert isinstance(expr, list)
    assert expr[0] in OPS, f"Unknown operation {expr[0]}"
    func = OPS[expr[0]]
    return func(env, expr[1:])


def main():
    assert len(sys.argv) == 2, "Usage: sol_arrays.py filename"
    with open(sys.argv[1], "r") as reader:
        program = json.load(reader)
    result = do({}, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
