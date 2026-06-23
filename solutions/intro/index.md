## Solutions

### Setting Up

The `ruff` linter watches for a wide range of problems: unused imports, undefined names, overly complex functions, and stylistic inconsistencies like trailing whitespace or the wrong number of blank lines between definitions. Installing it with `pip install ruff` and running `ruff check` on your own code almost always surfaces something you didn't notice.

Many of its reports are genuinely helpful---an undefined variable would crash your program at runtime, and an unused import slows startup and confuses readers. But some rules are more a matter of taste. The default line length limit of 88 characters (matching Black's default) can feel cramped if you work on a wide monitor. The rule that flags single-character variable names is sensible most of the time, but perfectly reasonable loop counters like `i` and `j` trigger it. When you disagree with a rule, you can silence it project-wide in `pyproject.toml` or per-line with a `# noqa: F841` comment. The point isn't to obey blindly; it's to make every deviation a conscious choice.

Here is a small script that creates two Python files with common problems and runs ruff on them so you can see what the linter reports without hunting through a large codebase.

[%inc sol_setting_up.py %]

### Avoiding Potholes

Open source projects track bugs and feature requests through issues, and reading a few open issues in the book's repository is a good way to learn what makes a report easy (or hard) for a maintainer to act on. The most approachable issues share a few traits: a one-line title that describes the symptom rather than the suspected cause, a numbered list of steps that reproduce the problem, a snippet showing what the reporter expected to see, and a snippet showing what actually happened. They also minimize background story---maintainers need the recipe, not the memoir.

The issues that are hard to understand usually omit one of those ingredients. A title like "It's broken" gives nobody a reason to click. A report that says "I clicked around and got an error" without the exact URL, the exact error message, and the exact input forces the maintainer to guess. Issues that mix several unrelated problems into one thread are also difficult because closing one half leaves the other dangling.

When you file an issue yourself, write the title last---after you have all the facts laid out, you will know the most specific way to describe the problem. Include the version of the software you are using, your operating system, and any configuration that might matter. If you can, reduce the problem to the smallest possible script or sequence of commands. That reduction often solves your problem before you even submit, and when it doesn't, it gives the maintainer a head start.

This script uses the GitHub API to fetch open issues from the book repository and prints a summary of each, focusing on the elements that make issues easy or hard to understand.

[%inc sol_avoiding_potholes.py %]

