"""A socketclient base class, analogous to socketserver's TCPServer/BaseRequestHandler.

The ``SocketClient`` class wraps the boilerplate of creating a socket,
connecting, sending data in chunks, and receiving a reply.  Users override
``make_message`` and ``handle_reply`` to define what gets sent and how the
response is interpreted.

In practice this pattern is less useful than the server-side equivalent
because client needs vary a lot (different message formats, different
reply-handling strategies), and most real applications reach for a
higher-level library like ``requests``.  For a simple file-transfer tool,
though, it keeps the main program tidy.
"""

import socket

CHUNK_SIZE = 1024


class SocketClient:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def run(self):
        """Connect, send a message, receive the reply, and return it."""
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self._host, self._port))
        message = self.make_message()
        self._send_all(conn, message)
        reply = self._receive_all(conn)
        conn.close()
        return self.handle_reply(reply)

    def make_message(self):
        """Override: return the bytes to send."""
        raise NotImplementedError

    def handle_reply(self, reply):
        """Override: process the server's reply bytes and return a result."""
        raise NotImplementedError

    def _send_all(self, conn, data):
        total = 0
        while total < len(data):
            sent = conn.send(data[total:])
            if sent == 0:
                break
            total += sent

    def _receive_all(self, conn):
        chunks = []
        while True:
            latest = conn.recv(CHUNK_SIZE)
            chunks.append(latest)
            if len(latest) < CHUNK_SIZE:
                break
        return b"".join(chunks)


class SendFileClient(SocketClient):
    """A concrete client that sends a file and checks the server's ack."""

    def __init__(self, host, port, filename):
        super().__init__(host, port)
        self._filename = filename

    def make_message(self):
        with open(self._filename, "rb") as reader:
            return reader.read()

    def handle_reply(self, reply):
        size_str = reply.decode("utf-8")
        return int(size_str)


class FakeSocket:
    """Pretends to be a connected socket for testing purposes."""

    def __init__(self, server_data):
        self._server_data = server_data
        self._sent = []
        self._recv_pos = 0

    def connect(self, address):
        pass

    def send(self, data):
        self._sent.append(data)
        return len(data)

    def recv(self, max_bytes):
        top = min(len(self._server_data), self._recv_pos + CHUNK_SIZE)
        result = self._server_data[self._recv_pos:top]
        self._recv_pos = top
        return result

    def close(self):
        pass


if __name__ == "__main__":
    # Quick smoke test with fake sockets.
    import tempfile, os

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("hello")
        tmpname = f.name

    try:
        client = SendFileClient("localhost", 8080, tmpname)
        client._send_all = lambda conn, data: None  # no-op for test
        msg = client.make_message()
        assert msg == b"hello", f"expected b'hello', got {msg!r}"
        assert client.handle_reply(b"5") == 5
        print("OK: SendFileClient works correctly")
    finally:
        os.unlink(tmpname)
