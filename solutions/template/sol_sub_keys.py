"""Solution: Sub-keys exercise.

Extend the template expander so that a variable name like `person.name`
looks up the "name" value in a dictionary called "person" in the current
environment.
"""

from env import Env as OriginalEnv


class Env(OriginalEnv):
    """Extended environment that supports dotted variable names."""

    def find(self, name):
        if "." in name:
            parts = name.split(".")
            value = None
            for frame in reversed(self.stack):
                if parts[0] in frame:
                    value = frame[parts[0]]
                    break
            if value is None:
                return None
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        return super().find(name)


def main():
    env = Env({"person": {"name": "Alice", "city": "Oxford"}})
    print("person.name:", env.find("person.name"))
    print("person.city:", env.find("person.city"))
    print("person.age (missing):", env.find("person.age"))
    print("plain var:", env.find("person"))


if __name__ == "__main__":
    main()
