"""Demonstrate do_func that accepts an optional name as the first argument."""


def env_set(env, name, value):
    env[-1][name] = value


def do_func(env, args):
    """Define a function, optionally naming it.

    With 2 args: params and body, returns a function value.
    With 3 args: name, params, and body, stores the function and returns it.
    """
    if len(args) == 3:
        name = args[0]
        params = args[1]
        body = args[2]
        func = ["func", params, body]
        env_set(env, name, func)
        return func
    else:
        assert len(args) == 2
        params = args[0]
        body = args[1]
        return ["func", params, body]


# Two-argument form: define anonymously, then assign.
env = [{}]
func_val = do_func(env, [["num"], ["get", "num"]])
print("anonymous function:", func_val)
env_set(env, "same", func_val)
print("env after manual set:", env)

# Three-argument form: define and name in one step.
env2 = [{}]
result = do_func(env2, ["double", ["num"], ["add", ["get", "num"], ["get", "num"]]])
print("named function stored:", result)
print("env after named definition:", env2)
