"""Solution: Drawing Borders — render elements with +, -, | borders."""


def draw_border(text):
    """Wrap a single-line string with a +-...-+ / |...| / +-...-+ border."""
    width = len(text)
    top_bottom = "+" + "-" * width + "+"
    middle = "|" + text + "|"
    return "\n".join([top_bottom, middle, top_bottom])


def bordered_render(node, fill_char="x"):
    """Return the bordered rendering of a block of text.

    This is a simplified stand-alone demonstration; in the full layout engine
    you would integrate border drawing into the ``render`` method so that each
    element draws its border plus its content, with children nested inside.
    """
    return draw_border(node)


class BorderedBlock:
    """A block that renders with a border."""

    def __init__(self, text):
        self.text = text

    def get_width(self):
        return len(self.text) + 2  # borders add 2 characters

    def get_height(self):
        return 3  # top border, content, bottom border

    def render(self, screen, x0, y0, fill):
        width = len(self.text)
        top_bottom = "+" + "-" * width + "+"
        middle = "|" + self.text + "|"
        lines = [top_bottom, middle, top_bottom]
        for iy, line in enumerate(lines):
            for ix, ch in enumerate(line):
                if 0 <= y0 + iy < len(screen) and 0 <= x0 + ix < len(screen[0]):
                    screen[y0 + iy][x0 + ix] = ch


def make_screen(width, height):
    return [[" "] * width for _ in range(height)]


def render_block(block):
    w = block.get_width()
    h = block.get_height()
    screen = make_screen(w, h)
    block.render(screen, 0, 0, "x")
    return "\n".join("".join(row) for row in screen)


if __name__ == "__main__":
    # Stand-alone border.
    assert draw_border("text") == "+----+\n|text|\n+----+"

    # BorderedBlock rendering.
    block = BorderedBlock("hello")
    result = render_block(block)
    expected = "+-----+\n|hello|\n+-----+"
    assert result == expected, f"got:\n{result!r}"
    print("All border tests passed.")
