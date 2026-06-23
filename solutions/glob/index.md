## Solutions

### Looping

The Chain of Responsibility design gives each matcher a reference to the next matcher in line. An alternative is to have a top-level object that holds a plain list of matchers and iterates through them. This approach turns the implicit chain into an explicit list, which makes it easier to see the whole pattern at once and simplifies debugging: you can print the list and see every step.

The tradeoff is that each matcher now needs to return enough information for the top-level object to decide what to do next. In the chain version, each matcher calls `self.rest._match(text, end)` and gets back either a new position or `None`. In the list version, the matchers themselves become simpler — they just report where they matched — but the coordinator has to stitch things together. Fixed-length matchers like `Lit` return a single next position, while variable-length matchers like `Any` return a list of all possible next positions. The coordinator tries them in order and backtracks when a later matcher fails. Whether this is simpler or more complicated than the Chain of Responsibility depends on taste, but for patterns with many sub-patterns the list approach is often clearer.

[%inc sol_looping.py %]

### Length Plus One

The loop in `Any._match` runs from `start` to `len(text) + 1` because the `*` wildcard can match zero or more characters. When `i` equals `len(text)`, we are testing whether the rest of the pattern can match an empty suffix — in other words, whether the `*` consumes the entire remaining string and the matchers after it are satisfied with nothing left. The `+ 1` ensures we try that case. Without it, a pattern like `a*` would never match `"a"` when the `*` is followed by `Null`, because the loop would stop at `i = 1` (the last character) and never try `i = 2` (the position after the last character, where `Null._match` would return the end of the string).

[%inc sol_length_plus_one.py %]

### Find One or More

The `+` operator matches *one or more* characters, unlike `*` which matches *zero or more*. We can implement this by requiring at least one character to be consumed before delegating to the rest of the chain. The implementation starts matching at `start + 1` instead of `start`, and otherwise works exactly like `Any`.

[%inc sol_find_one_or_more.py %]

### Match Sets of Characters

A character-set matcher checks whether the next character in the target string belongs to a given set. The `Charset` class stores the allowed characters and succeeds if `text[start]` is one of them. A `Range` matcher is a convenience that expands a character range into a `Charset` internally: `Range("a", "z")` is equivalent to `Charset("abcdefghijklmnopqrstuvwxyz")`.

[%inc sol_match_sets_of_characters.py %]

### Exclusion

A `Not` matcher succeeds only when the pattern it wraps fails to match. It tries the inner pattern at the current position; if the inner pattern reports success, `Not` fails. If the inner pattern fails, `Not` passes control to the rest of the chain without consuming any characters. This is trickier than it first appears because the inner pattern might match different amounts of text — we must check *all* possible matches of the inner pattern and fail only if one of them allows the overall match to succeed.

[%inc sol_exclusion.py %]

### Make Repetition More Efficient

The original `Any` matcher restarts the search for every possible split point, which means it re-checks the same suffixes many times. A more efficient approach is to try matching from right to left: start by assuming the `*` consumes everything, then gradually give characters back to the rest of the pattern. This way each suffix is tested exactly once.

[%inc sol_make_repetition_more_efficient.py %]

### Multiple Alternatives

The two-way `Either` class can be generalized to handle any number of alternatives by storing a list of patterns instead of separate `left` and `right` attributes. When no sub-patterns are specified, the matcher should fail immediately — an empty set of alternatives can never match anything, which is consistent with how alternation works in most pattern languages.

[%inc sol_multiple_alternatives.py %]

### Returning Matches

Instead of returning just `True` or `False`, we can return a data structure that records which substrings matched which parts of the pattern. Each matcher returns a list of `(name, substring)` pairs, where `name` identifies the matcher and `substring` is the text it consumed. The top-level `match` method aggregates these pairs. This is the foundation of how real regular expression libraries support capture groups.

[%inc sol_returning_matches.py %]

### Alternative Matching

Lazy matching makes `*` consume as few characters as possible; greedy matching makes it consume as many as possible. The change is straightforward: loop from the end of the string backward instead of from the start forward, so the `*` gobbles up everything before gradually giving characters back. Combined with the capture mechanism from the previous exercise, you can see exactly which characters each part of the pattern consumed.

[%inc sol_alternative_matching.py %]

