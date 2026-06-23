## Solutions

### Comparing Semantic Versions

The trick to sorting semantic versions is to break each one into its three
numeric components and compare those as integers rather than comparing the
strings as decimals.  If we compare `"2.1"` and `"1.99"` as strings, `"2.1"`
comes first because the character `'2'` is less than the character `'1'`—but
that is wrong.  The correct approach is to parse both strings into tuples
`(2, 1, 0)` and `(1, 99, 0)` and compare those element by element.

The script below uses Python's `sorted` with a `key` function that calls
`split(".")` and converts each part to an integer.  Versions with fewer than
three parts are padded with zeros, which handles both two-part versions like
`2.1` and three-part versions like `1.0.0` in the same list.

[%inc sol_comparing_semantic_versions.py %]

### Parsing Semantic Versions

A proper semver parser handles more than just MAJOR.MINOR.PATCH.  The full
specification includes pre-release labels (like `1.0.0-alpha.1`) and build
metadata (like `1.0.0+build.2024`).  Pre-release versions sort *before* the
corresponding release version, and numeric pre-release identifiers are
compared numerically while alphanumeric ones are compared lexically.

The script below defines a `SemVer` class with a regex-based parser and full
ordering support.  It handles the core format as well as pre-release and build
metadata, and it implements the comparison rules from the specification:
numeric identifiers in pre-release labels are compared by value, not as
strings, so `alpha.1` sorts before `alpha.10`.

[%inc sol_parsing_semantic_versions.py %]

### Using Scoring Functions

The scoring function described in the exercise multiplies version-component
differences by descending powers of ten: 100 for major, 10 for minor, and 1
for patch.  This ensures that a difference of one major version always
outweighs any number of minor or patch differences—exactly the opposite of
lexicographic ordering.

The script below defines `version_distance` and `total_distance`, then runs
them against the three valid combinations from the chapter's `triple.json`
example.  The combination `A.3 B.3 C.2` scores zero because it already
contains the newest version of every package.  The combination `A.2 B.2 C.2`
scores 1 in the major component for A and B, giving a total distance of
200—much worse.

But minimising distance from the newest versions does not always solve the
original problem.  The newest versions may have undiscovered bugs, and a team
that values stability over freshness might prefer the oldest compatible set.
A scoring function encodes a policy choice, not an objective truth, and
different projects will want different functions.

[%inc sol_using_scoring_functions.py %]

### Regular Releases

Calendar-based versioning makes package management easier in one important
way: you can tell at a glance how old a release is and whether you are due
for an upgrade.  There is no ambiguity about whether `2024.2` is "newer" than
`2023.4`—the answer is baked into the numbers.  It also eliminates arguments
about what constitutes a major versus a minor change, since version numbers
are assigned by the calendar rather than by human judgment.

On the other hand, calendar-based versioning makes package management harder
because the version number carries no signal about backward compatibility.  A
package that jumps from `2024.1` to `2024.2` might have breaking changes or
it might not—you cannot tell from the version alone.  Dependency ranges like
`>=2.0, <3.0` stop making sense, so package managers lose the ability to
express compatibility windows in a machine-readable way.  Security patches
can also get lost among regularly scheduled releases, and users who only want
bug fixes may have to absorb feature changes they did not ask for.

The demonstration script shows how simple CalVer sorting and generation can
be, and it enumerates these trade-offs in its output.

[%inc sol_regular_releases.py %]

### Searching Least First

The "fewest available versions first" heuristic is a straightforward
application of the most-constrained-variable principle from constraint
programming.  If package C has only two versions while packages A and B each
have three, we should decide on C first because there are fewer ways to go
wrong.  In the `triple.json` example, C has two versions, A and B each have
three, so we search C first.

For the small examples in this chapter the heuristic does not change the
number of candidates examined by much—the search space is so tiny that almost
any ordering works.  But as the number of packages grows, and especially when
some packages have dozens of versions while others have only a handful,
tackling the constrained packages first can prune large branches of the
search tree early.  The benefit is analogous to the difference between
sorting the input to a greedy algorithm and feeding it in random order:
sometimes it is the difference between finishing in milliseconds and
finishing never.

The script below reads the manifest from standard input, sorts the package
list by version count, and runs the incremental search from the chapter in
that order.

[%inc sol_searching_least_first.py %]

### Using Exclusions

The exclusion-based solver inverts the usual dependency model.  Instead of
declaring which versions of Green Red 1.2 *requires*, we declare which
versions it *excludes*.  The function `build_exclusions` converts a standard
requirements manifest into this form by computing, for each package+version,
the set of dependent versions that are *not* in the allowed list.

Package managers are not built this way because exclusions scale poorly.  In
a requirements-based model, a package author states which versions they have
tested against—typically a handful.  In an exclusions-based model, the author
would need to list every version they have *not* tested against, which grows
without bound as new versions of dependencies are released.  A package
published today would become incompatible with tomorrow's releases of its
dependencies unless the author continuously updates the exclusion list.  The
requirements model is *open-world*: new versions are assumed compatible until
proven otherwise.  The exclusions model is *closed-world*: new versions are
assumed incompatible until explicitly allowed, which is the opposite of how
most ecosystems evolve.

[%inc sol_using_exclusions.py %]

### Generating Constraints

The manual Z3 encoding from the chapter is repetitive: every package needs
its own Boolean variables, mutual-exclusion clauses, and dependency
implications.  The script below automates all of that.  Given any JSON
manifest in the chapter's format, `generate_constraints` creates the
variables and populates a solver with the three families of constraints:
at-least-one, mutual exclusion, and inter-package dependencies.

The helper `find_all_solutions` then enumerates every satisfying model by
repeatedly solving and excluding the previous solution, exactly as the
chapter's `z3_complete.py` does.  The main function ties them together so you
can pipe `triple.json` into the script and see all three valid combinations.

[%inc sol_generating_constraints.py %]

### Buildability

The build rules from the build chapter use a different kind of dependency
graph than the package manager: each node depends on other nodes being built
first, but there are no version numbers to choose among.  We can still use
Z3, but instead of Boolean variables representing whether a particular
version is selected, we use integer variables representing each node's
position in the build sequence.

The solver enforces three rules: every position is distinct, every position
is in the range 0 to N-1, and if node A depends on node B then A's position
must be greater than B's position.  Given an acyclic graph the solver finds a
model and we sort the nodes by position to get the build order.  Introduce a
circular dependency—say, making B depend back on A—and the solver reports
UNSAT, confirming that no topological ordering exists.

This is overkill for build ordering, where a simple topological sort does the
job in linear time.  But it illustrates how the same theorem-proving
machinery can handle structurally different problems once you learn to
express constraints in the solver's language.

[%inc sol_buildability.py %]
