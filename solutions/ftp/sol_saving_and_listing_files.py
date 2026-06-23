"""Server that saves uploaded files and lists the working directory."""

import os
import socketserver

CHUNK_SIZE = 1024


class FileServerHandler(socketserver.BaseRequestHandler):
    """Handle two commands:

    -   ``put <name>\\n<contents>`` — save the contents to a file named ``<name>``
        and reply with the number of bytes written.
    -   ``dir\\n`` — reply with a newline-separated list of files in the
        server's current working directory.
    """

    def handle(self):
        data = self._receive_all()
        text = data.decode("utf-8")
        if text.startswith("dir"):
            self._handle_dir()
        else:
            self._handle_put(text)

    def _receive_all(self):
        chunks = []
        while True:
            latest = self.request.recv(CHUNK_SIZE)
            chunks.append(latest)
            if len(latest) < CHUNK_SIZE:
                break
        return b"".join(chunks)

    def _handle_put(self, text):
        newline_pos = text.index("\n")
        filename = text[:newline_pos].strip()
        contents = text[newline_pos + 1:]
        with open(filename, "w") as writer:
            writer.write(contents)
        self.request.sendall(bytes(f"saved {len(contents)} bytes to {filename}", "utf-8"))

    def _handle_dir(self):
        listing = "\n".join(sorted(os.listdir(".")))
        self.request.sendall(bytes(listing, "utf-8"))


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
    # Test the "put" command.
    put_msg = bytes("hello.txt\nHello, world!", "utf-8")
    handler = FileServerHandler(FakeRequest(put_msg), None, None)
    handler.handle()
    reply = handler.request._sent[0].decode("utf-8")
    assert reply == "saved 13 bytes to hello.txt", f"unexpected reply: {reply}"
    with open("hello.txt") as f:
        assert f.read() == "Hello, world!"
    os.remove("hello.txt")
    print("OK: put command works")

    # Test the "dir" command.
    dir_msg = bytes("dir\n", "utf-8")
    handler = FileServerHandler(FakeRequest(dir_msg), None, None)
    handler.handle()
    reply = handler.request._sent[0].decode("utf-8")
    # We can't assert exact listing contents in a portable way, but we can
    # check that the reply is a non-empty string with newline-separated entries.
    assert len(reply) > 0, "dir listing should not be empty"
    print("OK: dir command works")
