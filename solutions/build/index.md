## Solutions

### Stable Sorting

Sets in Python are unordered collections. When you iterate over a set,
the order of elements is not guaranteed — it depends on the hash values of
the objects, which can vary between runs (especially with hash
randomization enabled). This makes testing code that uses sets difficult:
a topological sort that collects available nodes into a set and then
extends the result list with that set will produce an unpredictable
ordering. A test that asserts a specific output order will sometimes pass
and sometimes fail for no reason related to correctness.

The fix, as the chapter shows, is to sort the available nodes before
adding them to the result. This guarantees a deterministic output that
tests can rely on. The code below demonstrates both approaches side by
side.

[%inc sol_stable_sorting.py %]

### Checking Schema

JSON Schema provides a declarative way to describe the shape of valid
JSON documents. Instead of writing manual checks for required keys and
types, we define a schema object and let the `jsonschema` library
validate the configuration against it. The schema below requires every
value in the top-level object to be a dict with string `rule` and array
`depends` keys. One thing JSON Schema cannot easily express is the
cross-reference constraint — that every dependency must also be a key in
the config — so we still check that manually. The code gracefully handles
missing the `jsonschema` package by falling back to a manual check.

[%inc sol_checking_schema.py %]

### Handling Failure

The exercise asks for three changes. First, each rule can specify
`"fail": true` to indicate that its recipe should fail. Second, when a
rule fails, other targets that do not depend (directly or indirectly) on
the failed one should still be built. Third, we need tests.

The implementation introduces a `BuildFailure` exception. During the
build loop, if a node's dependencies intersect the `failed` set we skip
it and mark it as failed (so transitive dependents are also skipped). If
a node's rule explicitly fails we catch the exception and record the
failure. The `main()` function runs through several scenarios: no
failures, an isolated failure, a failure that blocks a dependent, a
transitive failure through two levels, and circular dependency detection
still working.

[%inc sol_handling_failure.py %]

### Merging Files

The `build_from_files` method reads multiple JSON configuration files in
order and merges their targets into a single dictionary. When the same
target appears in more than one file, the last definition wins — this is
the simplest policy, and the code prints a warning so the user knows
about the conflict. After merging, the usual configure/sort/build
pipeline runs on the combined configuration. The demonstration creates
temporary files, merges them, and shows the conflict warning when a
target is redefined.

[%inc sol_merging_files.py %]

### Using Hashes

This solution has two parts. The `build_init` function scans every file
mentioned in a build configuration (targets and dependencies), computes
their SHA-256 hashes, and stores the mapping in `build_hash.json`. The
`BuildHash` class then uses those stored hashes to decide what to
rebuild: a target is stale if it has no stored hash, if it doesn't exist
on disk, or if any of its dependencies' current hashes differ from the
stored values. After building, it updates the hash file so the next run
has a fresh baseline. The demonstration creates files, initializes
hashes, confirms nothing needs rebuilding, then modifies a dependency
and shows that the dependent targets become stale.

[%inc sol_using_hashes.py %]

### Dry Run

A dry run walks the entire build graph and prints what *would* be done
without actually executing any recipes. The `build` method takes a
`dry_run` parameter; when true, it prints each action prefixed with
`[DRY RUN]` and returns an empty action list. When false, it executes
normally. This is a small change — really just an `if` statement
inside the build loop — but it gives users a safe way to preview what a
build will do before committing to it.

[%inc sol_dry_run.py %]

### Phony Targets

A phony target is marked with `"phony": true` in the configuration. It
doesn't correspond to a file on disk, so staleness checks based on
timestamps or hashes don't apply — phony targets always run when
requested. The `_check` method defaults `phony` to `False` and the
`_refresh` method prints a `[PHONY]` label when executing a phony
target's rule. A common use is a `test` target that depends on the
compiled program and runs the test suite.

[%inc sol_phony_targets.py %]

### Multiple Build Files

This solution adds an `import` key to build files. When the build
manager loads a config file, it checks for this key, recursively loads
each imported file (resolving paths relative to the importing file), and
merges all the definitions. Targets defined in the importing file
override those from imports. Circular imports are detected by tracking
the set of absolute paths seen during the load: if we encounter a path
already in the chain, we raise a `ValueError` with the full cycle
description.

[%inc sol_multiple_build_files.py %]
