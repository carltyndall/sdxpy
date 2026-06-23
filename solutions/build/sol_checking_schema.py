"""
Rewrite the configuration validator to use JSON Schema via the `jsonschema` module.
"""

import json
import sys

try:
    import jsonschema
except ImportError:
    jsonschema = None


BUILD_RULE_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^.*$": {
            "type": "object",
            "properties": {
                "rule": {"type": "string"},
                "depends": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["rule", "depends"],
            "additionalProperties": False,
        }
    },
}

CROSS_REF_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^.*$": {
            "type": "object",
            "properties": {
                "rule": {"type": "string"},
                "depends": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["rule", "depends"],
        }
    },
    "additionalProperties": False,
}


def validate_with_json_schema(config):
    """Validate build config against JSON Schema. Returns a dict of errors
    keyed by target name, or an empty dict if valid."""
    errors = {}

    # First, check the structure against the basic schema
    try:
        jsonschema.validate(instance=config, schema=BUILD_RULE_SCHEMA)
    except jsonschema.ValidationError as exc:
        return {"_schema": str(exc.message)}

    # Second, check that all mentioned dependencies exist as targets
    known = set(config.keys())
    for name, details in config.items():
        for dep in details.get("depends", []):
            if dep not in known:
                errors.setdefault(name, []).append(
                    f"unknown dependency '{dep}'"
                )

    return errors


class BuildSchema:
    """A BuildBetter-compatible class that uses JSON Schema for validation."""

    def __init__(self):
        if jsonschema is None:
            raise ImportError(
                "jsonschema is not installed. "
                "Install it with: pip install jsonschema"
            )

    def build(self, config):
        config = self._configure(config)
        ordered = self._topo_sort(config)
        actions = []
        for node in ordered:
            self._refresh(config, node, actions)
        return actions

    def _refresh(self, config, node, actions):
        assert node in config, f"Unknown node {node}"
        actions.append(config[node]["rule"])

    def _must(self, condition, message):
        if not condition:
            raise ValueError(message)

    def _configure(self, config):
        # Validate with JSON Schema first
        errors = validate_with_json_schema(config)
        if errors:
            messages = []
            for target, issues in errors.items():
                if target == "_schema":
                    messages.append(f"Schema error: {issues}")
                else:
                    for issue in issues:
                        messages.append(f"{target}: {issue}")
            raise ValueError("\n".join(messages))

        known = set(config.keys())
        return {
            n: self._check(n, d, known)
            for n, d in config.items()
        }

    def _check(self, name, details, known):
        # The schema already checked keys and types; just check cross-refs
        depends = set(details["depends"])
        self._must(
            depends.issubset(known),
            f"Unknown depends for {name}",
        )
        result = details.copy()
        result["depends"] = depends
        return result

    def _topo_sort(self, config):
        graph = {n: config[n]["depends"] for n in config}
        result = []
        while graph:
            available = {n for n in graph if not graph[n]}
            self._must(
                available,
                f"Circular graph {list(graph.keys())}",
            )
            result.extend(sorted(available))
            graph = {
                n: graph[n] - available
                for n in graph
                if n not in available
            }
        return result


def main():
    if jsonschema is None:
        print("jsonschema not installed. Install with: pip install jsonschema")
        print("Showing validation logic without running it.")
        # Show a manual check instead
        config = json.loads(sys.stdin.read())
        known = set(config.keys())
        for name, details in config.items():
            if not isinstance(details, dict):
                print(f"ERROR: {name} is not a dict")
                continue
            if "rule" not in details:
                print(f"ERROR: {name} missing 'rule'")
            if "depends" not in details:
                print(f"ERROR: {name} missing 'depends'")
            else:
                for dep in details["depends"]:
                    if dep not in known:
                        print(f"ERROR: {name} depends on unknown '{dep}'")
        print("Validation complete.")
        return

    # Try with a valid config
    valid_config = {
        "A": {"depends": ["B"], "rule": "build A"},
        "B": {"depends": [], "rule": "build B"},
    }

    print("Valid config:")
    try:
        builder = BuildSchema()
        actions = builder.build(valid_config)
        print(f"  Actions: {actions}")
    except ValueError as e:
        print(f"  Error: {e}")

    # Try with an invalid config
    invalid_config = {
        "A": {"depends": ["C"], "rule": "build A"},
        "B": {"depends": [], "rule": "build B"},
    }

    print("\nInvalid config (missing dependency):")
    try:
        builder = BuildSchema()
        actions = builder.build(invalid_config)
        print(f"  Actions: {actions}")
    except ValueError as e:
        print(f"  Error: {e}")

    # Try with a malformed config
    malformed_config = {
        "A": {"depends": [], "rule": "build A"},
        "B": {"depends": []},
    }

    print("\nMalformed config (missing rule):")
    try:
        builder = BuildSchema()
        actions = builder.build(malformed_config)
        print(f"  Actions: {actions}")
    except ValueError as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    main()
