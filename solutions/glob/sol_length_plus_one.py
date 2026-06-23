"""Solution for the "Length Plus One" exercise.

Why does the upper bound of the loop in the final version of ``Any``
run to ``len(text) + 1``?
"""

from glob_null import Any, Lit, Null


def demonstrate():
    """Show why len(text) + 1 is needed.

    The loop runs from ``start`` to ``len(text) + 1`` because the ``*``
    wildcard matches zero or more characters.  When ``i == len(text)``
    the ``*`` has consumed the entire remaining string and the loop
    checks whether the rest of the pattern is satisfied with the empty
    suffix.  Without the ``+ 1`` a pattern like ``a*`` would never
    match ``"a"`` when ``*`` is the final matcher, because the loop
    would stop at ``i = 1`` (the last character index) and never try
    ``i = 2`` (the position *after* the last character, where
    ``Null._match`` returns the end-of-string position).
    """
    # This works because the loop tries i = len("a") = 1,
    # which is the position after the last character.
    assert Any().match("a")
    assert Any().match("")

    # With Lit after Any: a*b matches "ab" because the loop tries
    # i = 0 (Any consumes nothing, then Lit("b") matches "ab"[0:]="ab" — wait,
    # that would fail).  It tries i = 1 (Any consumes "a", Lit("b")
    # matches "b" at position 1) — success.
    assert Any(Lit("b")).match("ab")

    # Without +1 the loop would miss the case where Any consumes
    # everything and rest is Null.  Here is a simulation of the bug:
    text = "a"
    # Buggy loop: for i in range(0, len(text)):  # 0 only
    # Correct loop: for i in range(0, len(text) + 1):  # 0, 1
    for i in range(len(text) + 1):
        end = Null()._match(text, i)
        if end == len(text):
            print(f"Match succeeded when Any consumed {i} characters")
            break
    else:
        print("No match found (this would happen without the +1)")

    print("Demonstration complete")


if __name__ == "__main__":
    demonstrate()
