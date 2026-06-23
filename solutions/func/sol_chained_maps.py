"""Demonstrate using ChainMap for environment management in the interpreter."""

import json
import sys
from collections import ChainMap


def do_add(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    return left + right


def do_call(env, args):
    assert len(args) >= 1
    name = args[0]
    values = [do(env, a) for a in args[1:]]
    func = env_get(env, name)
    assert isinstance(func, list) and (func[0] == "func")
    params, body = func[1], func[2]
    assert len(values) == len(params)
    frame = dict(zip(params, values))
    new_env = env.new_child(frame)
    result = do(new_env, body)
    return result


def do_func(env, args):
    assert len(args) == 2
    params = args[0]
    body = args[1]
    return ["func", params, body]


def do_get(env, args):
    assert len(args) == 1
    return env_get(env, args[0])


def do_print(env, args):
    vals = [do(env, a) for a in args]
    print(*vals)
    return None


def do_seq(env, args):
    for a in args:
        result = do(env, a)
    return result


def do_set(env, args):
    assert len(args) == 2
    name = args[0]
    value = do(env, args[1])
    env_set(env, name, value)
    return value


OPERATIONS = {
    name.replace("do_", ""): func
    for (name, func) in globals().items()
    if name.startswith("do_")
}


def do(env, instruction):
    if not isinstance(instruction, list):
        return instruction
    op, args = instruction[0], instruction[1:]
    assert op in OPERATIONS
    return OPERATIONS[op](env, args)


def env_get(env, name):
    return env[name]


def env_set(env, name, value):
    env[name] = value


def main():
    # A minimal test program: define double(x) = x + x, call double(3).
    program = [
        "seq",
        ["set", "double", ["func", ["num"], ["add", ["get", "num"], ["get", "num"]]]],
        ["print", ["call", "double", 3]],
    ]
    env = ChainMap({})
    result = do(env, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
