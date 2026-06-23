"""Explain what would happen if do_func evaluated parameters immediately."""


# This is a *broken* do_func that evaluates parameters at definition time.
# It is here to demonstrate why this is a bad idea.
def do_func_wrong(env, args):
    assert len(args) == 2
    params = args[0]
    body = args[1]
    # WRONG: evaluate parameter names as if they were variables.
    evaluated_params = [do(env, p) for p in params]
    return ["func", evaluated_params, body]


def do(env, instruction):
    if not isinstance(instruction, list):
        return instruction
    op, args_op = instruction[0], instruction[1:]
    return OPERATIONS[op](env, args_op)


def do_get(env, args):
    for e in reversed(env):
        if args[0] in e:
            return e[args[0]]
    raise KeyError(f"Unknown variable {args[0]}")


OPERATIONS = {
    "get": do_get,
    "func": do_func_wrong,
}


env = [{"x": 10}]

# This would try to look up "num" as a variable in the current environment.
# Since "num" does not exist, it raises KeyError.
try:
    do_func_wrong(env, [["num"], ["get", "num"]])
except KeyError as e:
    print(f"Error: {e}")
    print("do_func tried to evaluate 'num' as a variable, but it does not exist.")
    print("Parameters must be stored unevaluated so they can be bound at call time.")
