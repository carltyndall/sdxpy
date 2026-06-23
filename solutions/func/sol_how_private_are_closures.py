"""Explain why lines 1 and 2 are the same but 3 and 4 differ in closure_list."""


def wrap(extra):
    def _inner(f):
        return [f(x) for x in extra]

    return _inner


odds = [1, 3, 5]
first = wrap(odds)
print("1.", first(lambda x: 2 * x))  # doubles [1, 3, 5]

odds = [7, 9, 11]  # reassigns odds to a NEW list
print("2.", first(lambda x: 2 * x))  # still doubles [1, 3, 5] (first's closure)

print("first still closed over the original list:", first(lambda x: x))

evens = [2, 4, 6]
second = wrap(evens)
print("3.", second(lambda x: 2 * x))  # doubles [2, 4, 6]

evens.append(8)  # mutates the SAME list second closed over
print("4.", second(lambda x: 2 * x))  # doubles [2, 4, 6, 8] (mutation visible)

print("second sees the mutated list:", second(lambda x: x))
print()
print("Reassignment creates a new object; the closure still references the old one.")
print("Mutation changes the existing object; all references see the change.")
