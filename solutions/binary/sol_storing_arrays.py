"""Solution for 'Storing Arrays' exercise.

Take a list of numbers, verify that every element shares the same
Python numeric type, then pack them into an ``array.array`` and
serialise the result with ``struct.pack``.
"""

import array
import struct


# Map Python types to array type codes and struct format characters.
_TYPE_MAP = {
    int: ("l", "l"),       # signed long (native size)
    float: ("d", "d"),     # double
}


def pack_list(values):
    """Pack a homogeneous list of numbers into a bytes object.

    Returns the packed bytes.  Raises ``TypeError`` if the list is
    empty, contains mixed types, or contains unsupported types.
    """
    if not values:
        raise TypeError("cannot pack an empty list")

    first_type = type(values[0])
    if first_type not in _TYPE_MAP:
        raise TypeError(f"unsupported type: {first_type.__name__}")

    array_code, struct_fmt = _TYPE_MAP[first_type]

    # Verify homogeneity.
    for v in values:
        if type(v) is not first_type:
            raise TypeError(
                f"mixed types: expected {first_type.__name__}, "
                f"found {type(v).__name__}"
            )

    # Build the array.
    arr = array.array(array_code, values)

    # Pack the entire array into bytes.
    count = len(values)
    packed = struct.pack(f"@{count}{struct_fmt}", *arr)
    return packed


if __name__ == "__main__":
    # Integers.
    int_bytes = pack_list([10, 20, 30])
    unpacked_ints = struct.unpack(f"@{len(int_bytes) // struct.calcsize('l')}l", int_bytes)
    print(f"Packed ints:   {list(unpacked_ints)}")

    # Floats.
    float_bytes = pack_list([1.5, 2.5, 3.5])
    unpacked_floats = struct.unpack(f"@{len(float_bytes) // struct.calcsize('d')}d", float_bytes)
    print(f"Packed floats: {list(unpacked_floats)}")

    # Error: empty list.
    try:
        pack_list([])
    except TypeError as e:
        print(f"Correctly caught: {e}")

    # Error: mixed types.
    try:
        pack_list([1, 2.0])
    except TypeError as e:
        print(f"Correctly caught: {e}")

    print("All tests passed.")
