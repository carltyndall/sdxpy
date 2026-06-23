"""Solution: Padding Elements — add blank space on all four sides of content."""


def pad_text(text, padding):
    """Return a list of strings with `padding` blank rows/columns around `text`.

    The returned value represents the visual result when rendered on a
    character grid.  Each element is a string of the same length.
    """
    inner_width = len(text)
    outer_width = inner_width + 2 * padding
    blank_line = " " * outer_width
    inner_line = " " * padding + text + " " * padding
    result = []
    for _ in range(padding):
        result.append(blank_line)
    result.append(inner_line)
    for _ in range(padding):
        result.append(blank_line)
    return result


class PaddedBlock:
    """A block that includes padding on all four sides."""

    def __init__(self, text, padding=1):
        self.text = text
        self.padding = padding

    def get_width(self):
        return len(self.text) + 2 * self.padding

    def get_height(self):
        return 1 + 2 * self.padding

    def render(self, screen, x0, y0, fill):
        padded = pad_text(self.text, self.padding)
        for iy, line in enumerate(padded):
            for ix, ch in enumerate(line):
                sy = y0 + iy
                sx = x0 + ix
                if 0 <= sy < len(screen) and 0 <= sx < len(screen[0]):
                    screen[sy][sx] = ch if ch != " " else " "


def make_screen(width, height):
    return [[" "] * width for _ in range(height)]


def render_block(block):
    w = block.get_width()
    h = block.get_height()
    screen = make_screen(w, h)
    block.render(screen, 0, 0, "x")
    return "\n".join("".join(row) for row in screen)


if __name__ == "__main__":
    block = PaddedBlock("text", padding=1)
    result = render_block(block)
    expected = "\n".join(["     ", " text", "     "])
    assert result == expected, f"got:\n{result!r}\nexpected:\n{expected!r}"

    # Also check the ex_padding.txt shape.
    assert len(result.split("\n")) == 3
    assert len(result.split("\n")[0]) == 6

    print("All padding tests passed.")
