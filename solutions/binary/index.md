## Solutions

### Adding Strings

The trick is to mimic the grade-school addition algorithm: process the
two strings from right to left, add the digits at each position along
with any carry from the previous column, and build the result from least
significant digit to most.  We reverse each input, zip them together
with zero-padding for the shorter string, and maintain an integer carry
that starts at zero.  The only Python built-in conversions we allow
ourselves are `ord(digit) - ord('0')` to turn a single character into
its numeric value and `chr(value + ord('0'))` to go back, because those
are character-code arithmetic, not string-to-int parsing.  Reversing the
final list of digits gives the answer in normal order.

[%inc sol_adding_strings.py %]

### File Types

PNG files start with an eight-byte magic number that identifies the
format regardless of the file extension.  In decimal those bytes are
`137 80 78 71 13 10 26 10`; the four bytes `80 78 71 13` spell "PNG"
in ASCII, while the other bytes help detect transmission corruption.
We open the file in binary mode, read the first eight bytes, and compare
them against the known signature.  If the file has fewer than eight
bytes we know it cannot be a PNG.

[%inc sol_file_types.py %]

### Converting Integers to Bits

For the integer-to-binary direction we repeatedly extract the least
significant bit with `n & 1`, prepend it to a string, and shift right
with `n >>= 1`.  Special-casing zero avoids returning an empty string.
The reverse direction walks the input string from left to right: for
each `'1'` we shift the accumulator left and OR in a 1; for each `'0'`
we just shift left.  Both functions use only bitwise operators and
character comparison---no call to `int()` or `bin()`.

[%inc sol_converting_integers_to_bits.py %]

### Encoding and Decoding

UTF-8 encodes each Unicode code point into one to four bytes depending
on its magnitude.  Code points below 128 stay in a single byte.  Values
up to 2047 use two bytes: the high byte starts `110` followed by five
bits, the low byte starts `10` followed by six bits.  Values up to
65535 use three bytes (leading `1110`), and everything above uses four
bytes (leading `11110`).  Every continuation byte begins `10xxxxxx`.

The decoder reverses this process: it reads the first byte, counts the
number of leading 1 bits to determine how many bytes belong to this
character, then extracts and reassembles the payload bits.  It reports
an error if a byte claims to be a continuation byte out of nowhere, if
the lead byte indicates more bytes than are available, or if a
continuation byte does not have the `10xxxxxx` pattern.

[%inc sol_encoding_and_decoding.py %]

### Storing Arrays

Python's `array` module stores homogeneous numeric values in contiguous
memory, and the `struct` module serialises them into byte strings.  Our
function first determines a common type for all elements (raising
`TypeError` if the list is empty or if types disagree), then creates an
`array.array` of that type, appends every element, and packs the
array's buffer with `struct.pack` using the appropriate format string.

[%inc sol_storing_arrays.py %]

### Performance

The `array` module stores raw C values without the Python object
overhead, but accessing an element boxes it into a Python `int` or
`float` on the fly.  This boxing cost adds up when we traverse every
element.  We measure the difference by creating a large list of
integers and an array of the same values, then timing a simple
accumulation loop with `time.perf_counter`.  Running the script shows
that the array version is typically slower by a factor of two or three
for element-by-element access, though it still wins on memory footprint
when that matters more than access speed.

[%inc sol_performance.py %]
