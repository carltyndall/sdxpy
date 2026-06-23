"""Demonstrate do_func with implicit sequence and naming-at-creation."""


def env_set(env, name, value):
    env[-1][name] = value


def do_func(env, args):
    """Define a function, with implicit seq and optional naming.

    With 2 positional groupings (2-arg form): params and body.
        If body is a single expression, use it directly.
        If multiple body expressions, wrap in ["seq", ...].
    With 3+ positional groupings (3+-arg form): name, params, body...body.
        Same body logic, plus the function is stored under name.
    """
    if len(args) == 2:
        params = args[0]
        body = args[1]
        return ["func", params, body]
    elif len(args) == 3 and isinstance(args[1], list):
        # Ambiguous: could be (name, params, body) or (params, body1, body2).
        # We distinguish by checking if args[1] is a list (it is the param list
        # in the named form).
        name = args[0]
        params = args[1]
        body = args[2]
        func = ["func", params, body]
        env_set(env, name, func)
        return func
    elif len(args) == 3:
        # Anonymous form with implicit seq: (params, body1, body2).
        params = args[0]
        body = ["seq"] + args[1:]
        return ["func", params, body]
    else:
        # len(args) >= 4: name, params, body-expr-1, body-expr-2, ...
        name = args[0]
        params = args[1]
        rest = args[2:]
        body = rest[0] if len(rest) == 1 else ["seq"] + rest
        func = ["func", params, body]
        env_set(env, name, func)
        return func


# Two-argument anonymous form.
env = [{}]
f = do_func(env, [["num"], ["get", "num"]])
print("anonymous (2 args):", f)

# Three-argument named form with single body.
env2 = [{}]
f2 = do_func(env2, ["double", ["num"], ["add", ["get", "num"], ["get", "num"]]])
print("named single body:", f2)
print("env:", env2)

# Three-argument anonymous form with implicit seq (two body expressions).
env_anon_seq = [{}]
f_anon = do_func(env_anon_seq, [
    ["num"],
    ["print", ["get", "num"]],
    ["add", ["get", "num"], ["get", "num"]],
])
print("anonymous implicit seq:", f_anon)

# Four-argument named form with implicit seq (two body expressions).
env3 = [{}]
f3 = do_func(env3, [
    "print_double",
    ["num"],
    ["print", ["get", "num"]],
    ["add", ["get", "num"], ["get", "num"]],
])
print("named implicit seq:", f3)
print("env:", env3)
