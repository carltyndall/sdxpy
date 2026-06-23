"""Solution: internal checks — defensive programming.

Demonstrates additional assertions and type hints that could be
added to the interpreter for defensive programming.

Added assertions beyond the originals:
- Arithmetic operands are numeric before computing.
- get received a string name before lookup.
- empty-list expressions are rejected.
- set receives a string name before assignment.

Type hints document the expected shapes of environments, expressions,
and return values.  Most argument-count checks can be expressed as
type hints only indirectly (e.g. through overloads or protocols),
so plain assert statements remain the clearest tool for those.
"""

import json
import sys
from typing import Any, Dict, List, Union


Environment = Dict[str, Any]
Expr = Union[int, str, List[Any]]


def do_abs(env: Environment, args: List[Expr]) -> int:
    assert len(args) == 1, "abs requires exactly 1 argument"
    val = do(env, args[0])
    assert isinstance(val, (int, float)), f"abs expects numeric, got {type(val)}"
    return abs(val)


def do_add(env: Environment, args: List[Expr]) -> int:
    assert len(args) == 2, "add requires exactly 2 arguments"
    left = do(env, args[0])
    right = do(env, args[1])
    assert isinstance(left, (int, float)), f"add: left operand is {type(left)}"
    assert isinstance(right, (int, float)), f"add: right operand is {type(right)}"
    return left + right


def do_get(env: Environment, args: List[Expr]) -> Any:
    assert len(args) == 1, "get requires exactly 1 argument"
    name = args[0]
    assert isinstance(name, str), f"get: name must be a string, got {type(name)}"
    assert name in env, f"Unknown variable '{name}'"
    return env[name]


def do_seq(env: Environment, args: List[Expr]) -> Any:
    assert len(args) > 0, "seq requires at least 1 argument"
    result = None
    for item in args:
        result = do(env, item)
    return result


def do_set(env: Environment, args: List[Expr]) -> Any:
    assert len(args) == 2, "set requires exactly 2 arguments"
    name = args[0]
    assert isinstance(name, str), f"set: name must be a string, got {type(name)}"
    value = do(env, args[1])
    env[name] = value
    return value


OPS: Dict[str, Any] = {
    name.replace("do_", ""): func
    for (name, func) in globals().items()
    if name.startswith("do_")
}


def do(env: Environment, expr: Expr) -> Any:
    if isinstance(expr, int):
        return expr
    assert isinstance(expr, list), f"expected list, got {type(expr)}"
    assert expr, "empty list is not a valid expression"
    assert expr[0] in OPS, f"Unknown operation '{expr[0]}'"
    func = OPS[expr[0]]
    return func(env, expr[1:])


def main() -> None:
    assert len(sys.argv) == 2, "Usage: sol_internal-checks.py filename"
    with open(sys.argv[1], "r") as reader:
        program = json.load(reader)
    result = do({}, program)
    print(f"=> {result}")


if __name__ == "__main__":
    main()
