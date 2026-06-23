"""Solution: more statements — print and repeat.

Adds print and repeat commands to the interpreter.
The repeat command handles zero-repeat correctly by initialising
result to None before the loop, so the doubling.tll and repeat_zero.tll
programs both work as expected.
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


def do_get(env, args):
    assert len(args) == 1
    assert isinstance(args[0], str)
    assert args[0] in env, f"Unknown variable {args[0]}"
    return env[args[0]]


def do_gt(env, args):
    assert len(args) == 2
    return do(env, args[0]) > do(env, args[1])


def do_if(env, args):
    assert len(args) == 3
    cond = do(env, args[0])
    choice = args[1] if cond else args[2]
    return do(env, choice)


def do_leq(env, args):
    assert len(args) == 2
    return do(env, args[0]) <= do(env, args[1])


def do_print(env, args):
    """Print values: ["print", ...values...]."""
    values = [do(env, a) for a in args]
    print(*values)
    return None


def do_repeat(env, args):
    """Repeat a body N times: ["repeat", count_expr, body].
    Handles zero-repeat correctly by initialising result before the loop."""
    assert len(args) == 2
    count = do(env, args[0])
    result = None
    for _ in range(count):
        result = do(env, args[1])
    return result


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
    assert len(sys.argv) == 2, "Usage: sol_more-statements.py filename"
    with open(sys.argv[1], "r") as reader:
        program = json.load(reader)
    result = do({}, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
