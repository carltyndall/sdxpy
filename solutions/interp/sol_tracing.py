"""Solution: tracing.

Adds a --trace command-line flag to the interpreter.
When enabled, each operation prints a message showing
the operation name, its arguments, and the result it produces.
"""

import json
import sys


TRACE = False


def trace(op, args, result):
    """Print a trace message when tracing is enabled."""
    if TRACE:
        print(f"{op}{args} => {result}")


def do_abs(env, args):
    assert len(args) == 1
    val = do(env, args[0])
    result = abs(val)
    trace("abs", args, result)
    return result


def do_add(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    result = left + right
    trace("add", args, result)
    return result


def do_get(env, args):
    assert len(args) == 1
    assert isinstance(args[0], str)
    assert args[0] in env, f"Unknown variable {args[0]}"
    result = env[args[0]]
    trace("get", args, result)
    return result


def do_print(env, args):
    values = [do(env, a) for a in args]
    print(*values)
    return None


def do_seq(env, args):
    for item in args:
        result = do(env, item)
    trace("seq", args, result)
    return result


def do_set(env, args):
    assert len(args) == 2
    assert isinstance(args[0], str)
    value = do(env, args[1])
    env[args[0]] = value
    trace("set", args, value)
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
    global TRACE
    args = sys.argv[1:]
    if args and args[0] == "--trace":
        TRACE = True
        args = args[1:]
    assert len(args) == 1, "Usage: sol_tracing.py [--trace] filename"
    with open(args[0], "r") as reader:
        program = json.load(reader)
    result = do({}, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
