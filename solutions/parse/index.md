## Solutions

### Escape Characters

The key change is in the tokenizer's `tok` method.
When we encounter a backslash,
we read the next character and append it directly to the current literal,
regardless of whether that character would normally be treated as special.
This means `\*` becomes part of a `Lit` token containing a literal asterisk,
and `\\` becomes a literal backslash.

We also need to check for a trailing backslash (one at the very end of the input
with no following character to escape), which should be flagged as an error.

After the backslash is processed we skip ahead by two positions (the backslash
and the escaped character) rather than the usual single step,
so we don't re-process the escaped character.

[%inc sol_escape_characters.py %]

### Character Sets

Character sets like `[xyz]` are a shorthand for `{x,y,z}`.
To support them we extend the tokenizer to emit `CharsetStart` and `CharsetEnd`
tokens when it sees `[` and `]`,
and we add a `_parse_CharsetStart` method to the parser that gathers
`Lit` tokens until it hits `CharsetEnd`, then wraps them in an `Either` node.

The tokenizer change is a two-line addition to the special-character dispatch:

[%inc sol_character_sets.py %]

The parser method mirrors the logic used for `EitherStart` but is more general
--- it collects as many `Lit` tokens as appear before the closing bracket:

```python
def _parse_CharsetStart(self, rest, back):
    children = []
    while back and back[0][0] == "Lit":
        children.append(Lit(back[0][1]))
        back = back[1:]
    if not children:
        raise ValueError("empty character set")
    if not back or back[0][0] != "CharsetEnd":
        raise ValueError("unclosed character set")
    return Either(children, self._parse(back[1:]))
```

### Negation

Negated character sets like `[!abc]` require three additions:
a new `Not` match node in the AST,
a `!` token emitted by the tokenizer,
and an extension to `_parse_CharsetStart` that checks whether the first token
after the opening bracket is `Not`.

The `Not` class stores a set of excluded characters rather than a list of
`Lit` children.
This makes it straightforward to implement the "match anything except these"
check later, and it clearly distinguishes negation from the `Either` case in
the AST.

[%inc sol_negation.py %]

The parser's `_parse_CharsetStart` method now peeks at the first token:

```python
negated = False
if back[0][0] == "Not":
    negated = True
    back = back[1:]

# ... gather Lit tokens as before ...

if negated:
    excluded = {c.chars for c in children}
    return Not(excluded, self._parse(back[1:]))
else:
    return Either(children, self._parse(back[1:]))
```

### Nested Lists

This exercise builds a small standalone parser rather than extending the glob
parser.
The grammar is simple: a list is brackets around comma-separated items,
where each item is either a number or another list.

The tokenizer reads digits to produce integers, skips whitespace,
and emits brackets and commas as single-character tokens.
The parser is a recursive descent that mirrors the grammar directly:
when it sees `[`, it starts a new list and recursively parses items
until it hits `]`.

[%inc sol_nested_lists.py %]

### Simple Arithmetic

This exercise requires operator precedence:
multiplication and division bind tighter than addition and subtraction.
The classic solution uses three mutually recursive functions,
each handling one precedence level.
`_expr` handles `+` and `-`,
`_term` handles `*` and `/`,
and `_factor` handles numbers and parenthesised sub-expressions.

The functions follow the same pattern:
parse a left operand at the next-higher precedence level,
then loop while the next token is an operator at the current level,
building a `[op, left, right]` tree node for each operation.
This naturally produces left-associative trees that respect precedence.

[%inc sol_simple_arithmetic.py %]

