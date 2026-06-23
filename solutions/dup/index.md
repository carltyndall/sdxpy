## Solutions

### Odds of Collision

Your colleague has added the odds in the table---but that is not how probability works.
The table shows the *conditional* probability of a collision on the next file
assuming no collision has happened yet.
To find the actual probability of at least one collision across four files,
we multiply the probabilities of *avoiding* a collision at each step
and subtract the result from one.

With 2-bit hashes there are four possible hash codes.
The first file always lands safely.
The second file avoids collision with probability 3/4
(it must pick one of the three unused values).
The third file avoids collision with probability 2/4,
and the fourth with probability 1/4.
The probability that *none* of the four files collide is therefore:

\[
1 \times \frac{3}{4} \times \frac{2}{4} \times \frac{1}{4}
= \frac{6}{64}
= \frac{3}{32}
\approx 0.09375
\]

So the probability of at least one collision is
\( 1 - \frac{3}{32} = \frac{29}{32} \approx 0.90625 \),
or about 90.6%.
That is quite a bit higher than the 75% your colleague claimed.
The same logic underlies the birthday problem discussed in this chapter:
collisions become likely much sooner than most people expect.

[%inc sol_odds_of_collision.py %]

### Streaming I/O

Reading an entire file into memory with `read()` works fine for small files,
but it can be wasteful---or impossible---for large ones.
A streaming API lets us feed data to the hash function one chunk at a time,
keeping memory use constant regardless of file size.

Python's `hashlib` hashing objects support an `update()` method for exactly this purpose.
We create a `sha256()` object,
read the file in fixed-size blocks (64 KB is a reasonable choice),
call `update()` on each block,
and then call `hexdigest()` to get the final hash.
The result is identical to hashing the entire file at once,
but our program never holds more than one chunk of the file in memory at a time.


[%inc sol_streaming_i_o.py %]

### Big Oh

In the introduction, "rapidly" means *quadratically*.
A system with \(N\) components has \(N(N-1)/2\) possible pairwise connections.
When \(N\) doubles,
the number of connections roughly quadruples---
from 10 components giving 45 pairs to 20 components giving 190 pairs,
and so on.
In big-oh terms this is \(O(N^2)\).
This is why understanding the interactions between components,
not just the components themselves,
is essential as systems grow.

The same \(O(N^2)\) pattern shows up whenever every element must be compared to every other element,
which is why hashing is such a powerful optimization:
it reduces the problem from \(O(N^2)\) to \(O(N)\) by grouping items before comparison.

[%inc sol_big_oh.py %]

### The `hash` Function

Python's built-in `hash` function returns an integer that represents an object's value,
and it only works on *hashable* objects.
An object is hashable if it is immutable---
its value cannot change after creation---
because the hash must remain stable for the lifetime of the object.
If an object's hash were to change after it was inserted into a dictionary,
the dictionary would no longer be able to find it.

Integers and strings are immutable.
The value `123` will always be `123`,
and the string `"123"` will always be `"123"`,
so `hash(123)` and `hash("123")` both succeed.
Lists, on the other hand, are mutable:
we can append, remove, or replace elements after creation.
If `hash([123])` were allowed and we later modified the list,
any dictionary using that list as a key would break.
Python therefore raises a `TypeError` with the message "unhashable type: 'list'"
whenever you try to hash a mutable collection.

[%inc sol_the_hash_function.py %]

### How Good Is SHA-256?

To check how evenly SHA-256 distributes hash codes,
we can hash each unique line of a text file,
convert the hexadecimal digests to integers,
and plot a histogram.
The script below does exactly that using Plotly for visualization.

When you run this on a large text file
you will see that the integer values are spread fairly uniformly
across the entire 256-bit space.
As the number of unique lines grows,
the histogram becomes flatter---
exactly what we expect from a cryptographic hash function.
The evenness of the distribution is why we can trust SHA-256
to keep files in separate groups:
collisions are spectacularly unlikely,
so files with the same hash are almost certainly identical.

[%inc sol_how_good_is_sha_256.py %]

