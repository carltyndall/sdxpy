## Solutions

### Handling Named Arguments

The `call` function shown in the chapter captures extra positional
arguments with `*args` and spreads them into the method.  Adding support
for named (keyword) arguments follows the same pattern: capture them
with `**kwargs` and spread them with `**kwargs`.  The change is
surprisingly small---you add two characters to the function signature
and two characters to the call site.  The real work is making sure every
method you write can accept and forward keyword arguments correctly,
especially when methods call other methods through `call`.  A nice
side-effect is that methods can now use keyword-only arguments (the kind
after a bare `*`) to make their interfaces more readable.

[%inc sol_handling_named_arguments.py %]

### Multiple Inheritance

Supporting multiple inheritance means replacing the single `_parent`
reference with a list (or tuple) of parents and deciding the order in
which they are searched.  A depth-first, left-to-right search is easy
to write but does *not* match Python's C3 linearization: it can visit
the same ancestor twice and does not guarantee that a child class is
checked before its parents.  A breadth-first approach gets closer to
Python's behaviour for simple hierarchies---it visits all direct parents
before any grandparent---and avoids the diamond problem in common cases.
The implementation uses a queue and a set of already-seen class ids to
prevent infinite loops.

[%inc sol_multiple_inheritance.py %]

### Class Methods and Static Methods

An *instance method* receives the object as its first argument---that is
the `thing` we have been passing explicitly in our `call` function.  A
*class method* receives the *class* (the dictionary holding the methods)
as its first argument; in real Python this is spelled `cls` by
convention.  A *static method* receives neither: it is just a plain
function that happens to live in a class namespace.

We can model class methods by adding a `call_class` helper that looks up
the method and passes the class dictionary as the first argument.
Static methods need no special support at all---you can pull them out of
the class dictionary and call them directly, or let `call_class` pass
the class argument knowing the function will ignore it.  The essential
difference is intent: a class method is for operations that need the
class but not an instance (like alternative constructors), while a
static method is for utility functions that are logically related to the
class but independent of any particular instance or the class itself.

[%inc sol_class_methods_and_static_methods.py %]

### Reporting Type

Python's `type` returns the most-specific class of an object, while
`isinstance` walks the inheritance chain to see whether an object is an
instance of a class or any of its ancestors.  Implementing both for our
dictionary-based system is straightforward.  `type_of` simply returns
the value of the `_class` key.  `is_instance_of` starts from that class
and follows `_parent` references until it either finds a match or hits
`None`.  The two functions together give us the same introspection
capabilities we rely on in real Python code.

[%inc sol_reporting_type.py %]

### Using Recursion

The iterative `find` uses a `while` loop to walk up the `_parent` chain.
A recursive version replaces the loop with a direct self-call.  The
base case---`cls is None`---raises `NotImplementedError`, and the
recursive case calls `find` on the parent.  This version has no mutable
variables and reads almost like a mathematical definition: *the method
is either in this class or in one of its ancestors*.  For shallow
inheritance chains (the normal case) the two versions are
indistinguishable in practice.  The recursive version would hit
Python's recursion limit if someone built a deliberately deep chain,
but that is more of a thought experiment than a real concern here.

[%inc sol_using_recursion.py %]

### Method Caching

Every call to a method in our system walks the inheritance chain, which
means inherited methods cost more to look up than methods defined
directly on the class.  A per-object cache eliminates this extra work
after the first call.  Each object gets a `_cache` dictionary; `call`
checks the cache before falling back to `find`, and writes the result
back into the cache on a miss.  The trade-off is straightforward: the
cache consumes a small amount of extra memory per object, but it turns
repeated method lookups from O(depth) operations into O(1) dictionary
lookups.  For programs that call the same method many times on the same
object, the speedup is real.  The added complexity is modest---three
extra lines in `call`---and the cache is transparent to the rest of the
system.

[%inc sol_method_caching.py %]

