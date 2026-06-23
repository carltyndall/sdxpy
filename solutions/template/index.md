## Solutions

### Tracing Execution

A trace directive helps with debugging by showing the current value of a
variable as the template is expanded.  We add a new handler for the
`z-trace` attribute that looks up the named variable in the environment and
prints its value to standard error.  The handler's `open` method outputs the
opening tag, prints the trace message, and returns `True` so recursion into
child nodes continues as usual.  The `close` method closes the tag.

Register the handler in the `HANDLERS` dictionary alongside the existing
ones and the directive `<span z-trace="varname"/>` will print `varname =
value` during expansion.

[%inc sol_tracing_execution.py %]

### Unit Tests

Testing template expansion is straightforward with pytest.  We test three
layers: the `Env` class for variable lookup and stack management, the
individual handlers for correct output, and the full `Expander` for
end-to-end correctness.  Each test constructs a small HTML fragment, runs it
through the expander with known input data, and asserts the exact output
string.  This catches regressions in handler logic, variable scoping, and
edge cases like missing variables or nested loops.

[%inc sol_unit_tests.py %]

### Sub-keys

The dot syntax `person.name` is a natural way to reach into nested data
structures.  We extend `Env.find` to split the requested name on `.` and
walk through nested dictionaries: look up the first segment, verify the
result is a dictionary, then look up the next segment inside it, and so on.
If any intermediate value is missing or isn't a dictionary, `find` returns
`None` as before.  This means `z-var="person.name"` in a template will
resolve through multiple levels of data without any changes to the handler
code.

[%inc sol_sub_keys.py %]

### Literal Text

When you are writing documentation *about* the template expander, you need a
way to show template directives without having them executed.  The
`z-literal` handler solves this: when it encounters a node with
`z-literal="true"`, it copies the entire subtree as raw HTML without
processing any directives inside.  The `open` method returns `False` to
prevent the visitor from recursing into child nodes, and instead calls
`node.decode_contents()` (a BeautifulSoup method) to get the raw inner HTML.
The `close` method outputs the closing tag.

The handler must be checked *before* other directive handlers so it takes
priority — otherwise a `z-var` inside a literal block would still be
expanded.

[%inc sol_literal_text.py %]

### Including Other Files

The `z-include` directive pulls content from another file into the current
template.  The handler's `open` method reads the named file, parses it with
BeautifulSoup, and walks the resulting tree using the same expander.  It
returns `False` to suppress normal child processing, since the included
content has already been walked.

The second part of the exercise asks about processing order.  If we include
raw text and then process, variables from the outer scope are visible inside
the included file — convenient but risky, because a variable name collision
can silently change behaviour.  If we process the included file first and
then insert the result, each file has its own variable scope and included
files behave more like self-contained components.  The handler below takes
the second approach by pushing a fresh environment frame before walking the
included content and popping it afterward, so the included file sees only
the variables explicitly passed to it.

[%inc sol_including_other_files.py %]

### HTML Snippets

Sometimes you want to capture a block of HTML and reuse it later in the same
template — a snippet.  The `z-snippet` handler stores the inner HTML of its
node as a string in the environment under the name given in the attribute.
Later uses of `z-var` with that name will insert the saved HTML.

The tricky part is that snippets may themselves contain template directives.
The handler captures the *unexpanded* inner HTML by calling
`node.decode_contents()` so that when a `z-var` later inserts the snippet,
the expander processes any directives inside it at that point.  This means
snippet expansion happens at the point of use, not the point of definition,
which is usually what you want.

[%inc sol_html_snippets.py %]

### YAML Headers

Many static site generators use YAML frontmatter to define per-page
variables.  We modify the main entry point to scan for a YAML header before
parsing the HTML.  A YAML header is a block of text at the very start of the
file delimited by lines containing exactly `---`.  We extract the text
between the delimiters, parse it with `yaml.safe_load`, and merge the
resulting dictionary into the variables passed to the expander.

If there is no YAML header the file is processed as before, so the change is
backward-compatible.  Variables defined in the YAML header override those
passed in from outside, which matches the principle that page-specific
settings should take precedence over global defaults.

[%inc sol_yaml_headers.py %]

### Expanding All Files

The `expand_all.py` script walks a source directory tree, finds every HTML
file, expands it with a shared set of variables, and writes the result to
the corresponding location under an output directory.  It uses `os.walk` to
traverse subdirectories and `pathlib` to construct output paths.  Each file
is expanded independently using the same variable dictionary, which can be
loaded from a JSON file passed as an optional third argument.

Creating parent directories with `os.makedirs` ensures the script works even
when the output tree doesn't exist yet.  The script processes files in
alphabetical order within each directory, which is deterministic but not
configurable — a real SSG would offer a sorting option.

[%inc sol_expanding_all_files.py %]

### Counting Loops

A counting loop iterates a fixed number of times, setting an index variable
to the current iteration number on each pass.  We add a handler for the
paired attributes `z-index` (the variable name to hold the counter) and
`z-limit` (the name of a variable whose integer value sets the upper bound).
The handler reads the limit from the environment, then loops from zero to
limit-minus-one, pushing a new frame with the index variable set for each
iteration and walking the children inside that frame.

This is cleaner than using `z-loop` over a pre-built list of numbers because
the template author doesn't need to construct `[0, 1, 2, ...]` in the
variable data — they just provide a number and the handler does the rest.

[%inc sol_counting_loops.py %]

### Boolean Expression

We extend `z-if` to support `and` and `or` operators in the condition
string.  The simplest approach is to split the attribute value on ` and `
and ` or ` and evaluate each part separately.  Our implementation handles
`and` by checking that every part is truthy and `or` by checking that at
least one part is truthy.  We look up each part as a variable name in the
environment, which means the condition must reference existing variables
rather than literal values.

A more complete solution would support nested expressions with parentheses
and literal comparisons, but this lightweight approach covers the most common
use cases without introducing a full expression parser.

[%inc sol_boolean_expression.py %]

### Element IDs

Hashing element content to generate IDs has one clear advantage: the ID is
deterministic and stable as long as the content doesn't change.  This means
bookmarks and cross-references survive rebuilds, and two pages that happen to
contain the same paragraph won't get colliding IDs.

The downsides are more numerous.  Identical content — such as a repeated
footer or a boilerplate disclaimer — produces the same hash, which defeats
the uniqueness requirement for HTML IDs.  Content changes (even fixing a
typo) break all references to that element.  Hashing is one-way, so you
cannot reverse an ID to discover what content it points to during debugging.
Finally, cryptographic hash functions are fast but not free; for a site with
thousands of pages, the cumulative cost is measurable.

In practice, most static site generators let authors specify IDs explicitly
in the source document and fall back to a slug derived from the heading text.
This gives authors control while still providing reasonable defaults.

[%inc sol_element_ids.py %]
