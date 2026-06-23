## Solutions

### Packing Null Bytes

The original `pack` method joins fields with null bytes (`\0`), so any
null byte inside a field breaks the round-trip.  The fix is to drop
delimiter-based framing and use *length-prefixed encoding* instead:
before each field we write its length as a decimal number followed by a
colon, then the field value itself.  A trailing newline marks the end of
the record so that `pack_multi` can still split records apart by looking
for newlines.

This encoding can represent any string value — even one that contains
colons or null bytes — because the parser always reads the length first
and then consumes exactly that many characters.  The trade-off is that
length-prefixed records are no longer fixed-size, so the database's
fixed-record-length assumptions would need to be revisited for a
production system.

[%inc sol_packing_null_bytes.py %]

### Packing in Binary

The exercise has three parts.

*Part 1: binary packing.*  We replace the text-based `pack` and `unpack`
methods with ones that use the `struct` module.  The format string
encodes the name as a fixed-length byte string, the timestamp as a
signed 64-bit integer, a byte count for the number of valid readings,
and that many signed 32-bit integers.  `struct.calcsize` gives us the
exact record size without manual arithmetic.

*Part 2: file I/O changes.*  Because `struct.pack` returns `bytes`, the
database's `_save` and `_load` methods must open files in binary mode
(`"wb"` / `"rb"`) instead of text mode.  Calls to `writer.write` and
`reader.read` now deal in `bytes` rather than `str`, which eliminates
any accidental encoding transformations at the file boundary.

*Part 3: should I/O move into the record class?*  No.  Packing is about
*serialisation* — turning an object into a portable representation.
File I/O is about *persistence* — putting bytes somewhere durable.
Keeping the two concerns in separate classes means the database can swap
storage backends (local files, a network socket, an object store) without
changing the record class, and the record class can change its binary
layout without touching the storage layer.  This is the single-responsibility
principle at work.

[%inc sol_packing_in_binary.py %]

### Implement Compaction

The cleanup code in the chapter removes entire blocks when every record
inside them is stale, but it does not remove stale records from within a
block that still contains some live records.  Compaction fixes that: we
walk every block, keep only the records whose sequence ID matches the
current index entry (i.e., the most recent version of each key), then
repack and rewrite each block.  After compaction we drop any blocks that
became empty and rebuild the index with fresh sequence IDs.

The implementation adds a `compact` static method that operates on an
existing `Compacted` database instance.  It filters each block's
dictionary to the set of live sequence IDs, removes trailing empty
blocks, reassigns contiguous sequence IDs, and writes the slimmed-down
blocks back to disk.

[%inc sol_implement_compaction.py %]

### Save the Index Separately

The original `BlockedFile._build_index` scans every block file on disk
to reconstruct the in-memory index — an O(num_blocks) operation.  We can
avoid that work by caching the index in a dedicated `index.dat` file
alongside the block files, writing it after every `add` and reading it
on startup.  The index is small (one entry per live record), so JSON is
a fine serialisation format for it.

The experiment in the solution script builds two databases with the same
records: one using the original `BlockedFile` and one using our new
`IndexedFile`.  It then measures restart (constructor) time for each
over ten runs after a few warm-up iterations.  For 100 records the
indexed variant is usually faster, and the gap widens as the number of
blocks grows because scanning every block file on startup becomes the
dominant cost.  One caveat: saving the index on every `add` means many
small writes, which could hurt write-heavy workloads.  Profiling with
realistic access patterns is essential before adopting this change in
production.

[%inc sol_save_the_index_separately.py %]
