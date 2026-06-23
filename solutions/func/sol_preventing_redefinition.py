"""Demonstrate preventing function redefinition in the interpreter."""


def env_set(env, name, value):
    env[-1][name] = value


def do(env, instruction):
    if not isinstance(instruction, list):
        return instruction
    op, args = instruction[0], instruction[1:]
    return OPERATIONS[op](env, args)


def do_get(env, args):
    for e in reversed(env):
        if args[0] in e:
            return e[args[0]]
    raise KeyError(f"Unknown variable {args[0]}")


def do_set(env, args):
    """Set a variable, preventing redefinition."""
    assert len(args) == 2
    name = args[0]
    if name in env[-1]:
        raise ValueError(f"Cannot redefine '{name}'")
    value = do(env, args[1])
    env_set(env, name, value)
    return value


OPERATIONS = {
    "get": do_get,
    "set": do_set,
}

env = [{}]

# First definition succeeds.
print("defining 'x' as 10...")
do_set(env, ["x", 10])
print("  ok, x =", env_get(env, ["x"]))

# Attempted redefinition raises an error.
print("attempting to redefine 'x' as 20...")
try:
    do_set(env, ["x", 20])
except ValueError as e:
    print(f"  blocked: {e}")

print("final env:", env)
