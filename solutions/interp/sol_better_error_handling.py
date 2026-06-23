"""Solution: better error handling.

Adds:
- TLLException: a custom exception class for TLL programs
- check(condition, message): raises TLLException when condition is false
- ["catch", body, ["handler", varname, ...handler_body...]]:
    executes body; if TLLException is raised, binds the error message
    to varname and executes handler_body
"""

import json
import sys


class TLLException(Exception):
    """Custom exception for TLL runtime errors."""
    pass


def check(condition, message):
    """Raise TLLException with *message* if *condition* is falsy."""
    if not condition:
        raise TLLException(message)


def do_abs(env, args):
    check(len(args) == 1, f"abs expects 1 argument, got {len(args)}")
    val = do(env, args[0])
    return abs(val)


def do_add(env, args):
    check(len(args) == 2, f"add expects 2 arguments, got {len(args)}")
    left = do(env, args[0])
    right = do(env, args[1])
    return left + right


def do_catch(env, args):
    """Catch TLLException: ["catch", body, ["handler", varname, ...handler_body...]]."""
    check(len(args) == 2, "catch expects 2 arguments")
    handler = args[1]
    check(isinstance(handler, list) and len(handler) >= 2 and handler[0] == "handler",
          "catch expects a handler list starting with 'handler'")
    handler_varname = handler[1]
    try:
        return do(env, args[0])
    except TLLException as exc:
        env[handler_varname] = str(exc)
        if len(handler) > 2:
            return do(env, ["seq"] + handler[2:])
        return None


def do_get(env, args):
    check(len(args) == 1, f"get expects 1 argument, got {len(args)}")
    check(isinstance(args[0], str), "get expects a string name")
    check(args[0] in env, f"Unknown variable '{args[0]}'")
    return env[args[0]]


def do_seq(env, args):
    for item in args:
        result = do(env, item)
    return result


def do_set(env, args):
    check(len(args) == 2, f"set expects 2 arguments, got {len(args)}")
    check(isinstance(args[0], str), "set expects a string name")
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
    check(isinstance(expr, list), f"expected list or int, got {type(expr)}")
    check(expr[0] in OPS, f"Unknown operation '{expr[0]}'")
    func = OPS[expr[0]]
    return func(env, expr[1:])


def main():
    assert len(sys.argv) == 2, "Usage: sol_better-error-handling.py filename"
    with open(sys.argv[1], "r") as reader:
        program = json.load(reader)
    result = do({}, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
