"""A server handler that collects chunks in a list instead of copying."""

import socketserver

CHUNK_SIZE = 1024


class EfficientHandler(socketserver.BaseRequestHandler):
    """Collect incoming chunks in a list and join them once at the end.

    The original implementation used ``data += latest`` inside the loop,
    which copies the growing string on every iteration.  This version
    appends each chunk to a list and calls ``b"".join`` after the loop,
    turning O(N^2) copying into O(N).
    """

    def handle(self):
        chunks = []
        while True:
            latest = self.request.recv(CHUNK_SIZE)
            chunks.append(latest)
            if len(latest) < CHUNK_SIZE:
                break
        data = b"".join(chunks)
        self.request.sendall(bytes(f"{len(data)}", "utf-8"))


class FakeRequest:
    """Pretends to be a socket so we can test without a real network."""

    def __init__(self, message):
        self._message = message
        self._position = 0
        self._sent = []

    def recv(self, max_bytes):
        top = min(len(self._message), self._position + CHUNK_SIZE)
        result = self._message[self._position:top]
        self._position = top
        return result

    def sendall(self, outgoing):
        self._sent.append(outgoing)


if __name__ == "__main__":
    # Send enough data to force multiple recv calls.
    message = b"x" * (CHUNK_SIZE * 3 + 7)
    handler = EfficientHandler(FakeRequest(message), None, None)
    handler.handle()
    result = handler.request._sent[0].decode("utf-8")
    expected = str(len(message))
    assert result == expected, f"expected {expected}, got {result}"
    print(f"OK: received {result} bytes (list-then-join works correctly)")
