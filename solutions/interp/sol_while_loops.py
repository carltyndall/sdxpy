"""Solution: while loops.

Adds a while-loop instruction: ["while", condition, body].
Evaluates the condition; if true, executes the body and repeats.
Uses a Python while loop internally for clarity.
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


def do_while(env, args):
    """While loop: ["while", condition, body].
    Repeatedly evaluates the body as long as condition is true.
    Returns the result of the last evaluation, or None if the body
    never executes."""
    assert len(args) == 2
    result = None
    while do(env, args[0]):
        result = do(env, args[1])
    return result


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
    assert len(sys.argv) == 2, "Usage: sol_while-loops.py filename"
    with open(sys.argv[1], "r") as reader:
        program = json.load(reader)
    result = do({}, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
