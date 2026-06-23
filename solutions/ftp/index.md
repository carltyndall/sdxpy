## Solutions

### Chunk Sizes

When the client sends zero bytes, the server's first call to `recv`
returns an empty byte string.  Since zero is less than `CHUNK_SIZE`,
the loop exits immediately and the server reports zero bytes received.

When the client sends exactly `CHUNK_SIZE` bytes, the server reads all
of them on the first `recv` call.  The next call returns an empty byte
string (the client has nothing left to send), so the loop breaks after
two iterations.

When the client sends `CHUNK_SIZE + 1` bytes, the first `recv` fills
its buffer with `CHUNK_SIZE` bytes.  The second `recv` picks up the
remaining single byte, which is less than `CHUNK_SIZE`, so the loop
exits.  The server correctly accumulates all the data in every case.

The script below uses a fake request object to exercise all three
scenarios without needing a real network connection.

[%inc sol_chunk_sizes.py %]

### Efficiency

The original `handle` method builds `data` with `data += latest` inside
the loop.  Every `+=` on a bytes object creates a new copy, so
receiving *N* chunks costs *O(N²)* time.  The fix is to append each
chunk to a list and call `b"".join(chunks)` after the loop finishes.
This copies each byte exactly once, giving *O(N)* total work.

The server shown below uses the list-then-join pattern.  The smoke test
at the bottom confirms that it correctly reassembles a multi-chunk
message.

[%inc sol_efficiency.py %]

### Saving and Listing Files

For the first part we change the protocol so the client sends the
destination filename, a newline, and then the file contents.  The
server splits the incoming data on the first newline to recover the
filename and writes everything after it to disk.  It replies with a
confirmation that includes the byte count and filename.

For the second part we add a `dir` command.  When the server receives
`dir\n` (with no other data), it calls `os.listdir(".")`, sorts the
result, joins the names with newlines, and sends the listing back to
the client.  The combined handler checks the first few bytes to decide
which operation to perform.

[%inc sol_saving_and_listing_files.py %]

### A Socket Client Class

The `socketserver` module provides `TCPServer` for the listening side
and `BaseRequestHandler` as a plug-in for processing requests.  We can
build a mirror-image abstraction for the sending side: a `SocketClient`
base class that handles connection setup, chunked sending, and reply
collection, leaving subclasses to override `make_message` and
`handle_reply`.

The `SendFileClient` subclass below reads a file and sends its contents
as the message.  In practice this pattern sees less use than its server
counterpart because client behaviour varies so widely — most real
projects reach for a library like `requests` — but it is a useful
exercise in symmetry and keeps small command-line tools tidy.

[%inc sol_a_socket_client_class.py %]
