"""Demonstrate server behavior with 0, CHUNK_SIZE, and CHUNK_SIZE+1 bytes."""

import socketserver

CHUNK_SIZE = 1024


class InspectHandler(socketserver.BaseRequestHandler):
    """A handler that reports how many recv calls it makes and what it sees."""

    def handle(self):
        data = bytes()
        calls = 0
        while True:
            latest = self.request.recv(CHUNK_SIZE)
            calls += 1
            data += latest
            if len(latest) < CHUNK_SIZE:
                break
        self.request.sendall(
            bytes(f"calls={calls} total={len(data)}", "utf-8")
        )


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


def test_case(label, data):
    handler = InspectHandler(FakeRequest(data), None, None)
    handler.handle()
    print(f"{label}: {handler.request._sent[0].decode('utf-8')}")


if __name__ == "__main__":
    # Zero bytes: recv returns b"" on first call, which is < CHUNK_SIZE,
    # so the loop breaks immediately with total=0.
    test_case("zero bytes", b"")

    # Exactly CHUNK_SIZE bytes: first recv gets all the data,
    # second recv returns b"" (end of stream), loop breaks.
    test_case("CHUNK_SIZE bytes", b"x" * CHUNK_SIZE)

    # CHUNK_SIZE+1 bytes: first recv gets CHUNK_SIZE bytes,
    # second recv gets the remaining 1 byte, loop breaks.
    test_case("CHUNK_SIZE+1 bytes", b"x" * (CHUNK_SIZE + 1))
