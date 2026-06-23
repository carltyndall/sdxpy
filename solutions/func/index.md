## Solutions

### Rewriting Environment Creation

The original line uses `zip` and `dict` together to build a stack frame
in a single expression:

[%inc sol_rewriting_environment_creation.py %]

Rewriting it with an explicit loop makes each step visible.  You create
an empty dictionary, walk through the parameter names and their
corresponding values in lockstep, and insert each pair one at a time.
Some people find the loop version easier to read because it spells out
*what* is happening without requiring the reader to remember the
behaviour of `zip` and `dict`.  Others prefer the original because it is
shorter and, once you are comfortable with `zip`, the intent is
unmistakable.  There is no single right answer---this is a matter of
taste and team convention.

```python
frame = {}
for param, value in zip(params, values):
    frame[param] = value
env.append(frame)
```

### Chained Maps

Python's `collections.ChainMap` groups multiple dictionaries so that
lookups automatically search through them in order.  It is a natural fit
for our call stack: instead of a list of dictionaries that we search
manually in `env_get` and `env_set`, we can wrap the frames in a single
`ChainMap`.  Lookups then happen from most recent to oldest frame
without any explicit loop, and setting a variable always writes into the
first (most recent) frame.  The `env` variable becomes a `ChainMap`
instead of a list, and `do_call` pushes a new frame by creating a new
`ChainMap` with the new frame as the first mapping and the old chain as
the child.  The interpreter's behaviour is identical, but the code is
shorter and delegates the scoping logic to the standard library.

[%inc sol_chained_maps.py %]

### Defining Named Functions

When `do_func` receives three arguments instead of two, we treat the
first as the function's name and store it directly in the environment
without needing a separate `"set"` instruction.  The second argument is
the parameter list and the third is the body.  This is a small
convenience that saves one level of nesting in the JSON representation.
The trade-off is that `do_func` now does two things---define the
function *and* assign it---which makes the semantics slightly harder to
describe.  For a toy interpreter it is a harmless shortcut; in a
production language you would keep definition and naming separate.

[%inc sol_defining_named_functions.py %]

### Evaluating Parameters

If `do_func` evaluated the parameter list immediately, it would try to
look up each parameter name as a variable in the current environment
before the function had ever been called.  Since those names do not
exist yet---the parameters are placeholders for values that will be
supplied later---the interpreter would either raise an `Unknown variable`
error or inadvertently bind the parameters to whatever values happen to
share those names in the calling scope.  Either outcome defeats the
purpose of function definition.  Storing parameters unevaluated is
essential: we need to remember the names so we can bind them to the
actual arguments at call time, not at definition time.

### Implicit Sequence

The first part of this exercise adds a convenient shorthand: if
`do_func` receives more than one body expression, it wraps them in an
implicit `"seq"` so the user does not have to write it explicitly.
Combining this with naming-at-creation from the previous exercise
creates an ambiguity when `do_func` receives exactly three arguments:
could be `(name, params, body)` for a named single-body function, or
`(params, body1, body2)` for an anonymous function with an implicit
sequence.  We resolve this by checking whether the second argument is a
list---parameter lists are always lists---to decide which form was
intended.  When `len(args)` is four or more, there is no ambiguity: the
first argument is the name, the second is the parameter list, and
everything after that is the body.  The two features compose cleanly
because a small type check on the second argument is enough to
disambiguate.

[%inc sol_evaluating_parameters.py %]

### Preventing Redefinition

We can prevent redefinition by checking whether a name already exists
in the environment before allowing `do_set` to overwrite it.  If the
name is already bound, we raise an error.  This makes programs easier to
reason about---you never have to worry that a function you defined early
in the program has been silently replaced by something else---but it
also makes the language less flexible.  You cannot shadow a built-in
with a stub during testing, and you cannot incrementally refine a
function in a REPL.  Most mainstream languages allow redefinition, and
the few that do not (like Erlang for variables) are often described as
surprising by newcomers.

[%inc sol_preventing_redefinition.py %]

### Generalizing Closure-Based Objects

Generalizing `make_object` to accept any number of named parameters is
straightforward: you replace the single `initial_value` parameter with
`**kwargs` and copy them into the `private` dictionary.  The `getter`
now takes a name and returns `private[name]`; the `setter` takes a name
and a value and writes into the dictionary.  What happens on a missing
key depends on your design choice.  A Pythonic `getter` would raise
`KeyError` (or use `private.get(name)` to return `None`), and a
Pythonic `setter` would insert the key whether or not it existed
before---this is what `dict.__setitem__` does.  The setter does not
check types because Python is dynamically typed and type-checking at
every assignment would be expensive and un-Pythonic.  If you want type
guards, you add them as explicit checks inside `setter`.

[%inc sol_generalizing_closure_based_objects.py %]

### What Can Change?

The failing program tries to reassign the *variable* `value` inside the
closure, but Python's scoping rules treat any variable assigned inside a
function as local unless declared `nonlocal`.  When `_inner` executes
`value += 1`, Python sees the assignment and creates a new local
variable called `value`, then tries to read it before it has been
initialized---hence the `UnboundLocalError`.

The succeeding program wraps the integer in a single-element list.  The
inner function never assigns to `value` itself; it only mutates
`value[0]`.  Since there is no assignment to the name `value`, Python
treats it as a closure variable and looks it up in the enclosing scope
as expected.  The difference is fundamental: *assignment* creates local
variables, but *mutation* does not.  In Python 3 you can also fix the
first version by adding `nonlocal value` at the top of `_inner`, which
tells Python to bind `value` from the enclosing scope.

### How Private Are Closures?

The two calls to `first` produce the same result because `first` closed
over the *list* `odds`, not over its *contents at definition time*.  The
closure stores a reference to the list object.  When we reassign `odds`
to a new list on line 7, that creates a different list object---but
`first` still holds a reference to the original `[1, 3, 5]`.  So the
second call still doubles `[1, 3, 5]`, producing the same output as the
first call.

The two calls to `second` produce different results because the list
`evens` is *mutated* between the calls.  `second` also holds a reference
to the list object, and when we append `8` to it, the closure sees the
change through that reference.  The list starts as `[2, 4, 6]` (first
call produces `[4, 8, 12]`) and then becomes `[2, 4, 6, 8]` (second
call produces `[4, 8, 12, 16]`).  The privacy of closures hides the
names we use to reach objects, not the objects themselves.  If you share
a mutable object, every holder of a reference can see changes made by
every other holder.
