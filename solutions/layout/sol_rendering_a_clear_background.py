"""Solution: Rendering a Clear Background — only block nodes show text; rows and
columns render empty space."""

from easy_mode import Block, Col, Row


class PlacedBlock(Block):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.x0 = None
        self.y0 = None

    def place(self, x0, y0):
        self.x0 = x0
        self.y0 = y0

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


class PlacedCol(Col):
    def __init__(self, *children):
        super().__init__(*children)
        self.x0 = None
        self.y0 = None

    def place(self, x0, y0):
        self.x0 = x0
        self.y0 = y0
        y_current = self.y0
        for child in self.children:
            child.place(x0, y_current)
            y_current += child.get_height()


class PlacedRow(Row):
    def __init__(self, *children):
        super().__init__(*children)
        self.x0 = None
        self.y0 = None

    def place(self, x0, y0):
        self.x0 = x0
        self.y0 = y0
        y1 = self.y0 + self.get_height()
        x_current = x0
        for child in self.children:
            child_y = y1 - child.get_height()
            child.place(x_current, child_y)
            x_current += child.get_width()


class ClearRenderable:
    """Mixin: only Block children fill with characters; containers stay blank."""

    def render(self, screen, fill):
        if not hasattr(self, "children"):
            for ix in range(self.get_width()):
                for iy in range(self.get_height()):
                    screen[self.y0 + iy][self.x0 + ix] = fill


class RenderedBlock(PlacedBlock, ClearRenderable):
    pass


class RenderedCol(PlacedCol, ClearRenderable):
    pass


class RenderedRow(PlacedRow, ClearRenderable):
    pass


def make_screen(width, height):
    return [[" "] * width for _ in range(height)]


def next_fill(fill):
    return "a" if fill is None else chr(ord(fill) + 1)


def draw(screen, node, fill=None):
    fill = next_fill(fill)
    node.render(screen, fill)
    if hasattr(node, "children"):
        for child in node.children:
            fill = draw(screen, child, fill)
    return fill


def render(root):
    root.place(0, 0)
    width = root.get_width()
    height = root.get_height()
    screen = make_screen(width, height)
    draw(screen, root)
    return "\n".join("".join(ch) for ch in screen)


if __name__ == "__main__":
    fixture = RenderedCol(
        RenderedBlock(1, 2),
        RenderedRow(RenderedBlock(2, 1), RenderedBlock(1, 1)),
    )
    result = render(fixture)
    # Only blocks draw their character; row/col interiors stay spaces.
    # Block(1,2) at (0,0): "a" in (0,0) and (0,1)
    # Row at (0,2): contains Block(2,1) at (0,2)="b","b" and Block(1,1) at (2,2)="c"
    expected = "\n".join(["a ", "a ", "bbc"])
    assert result == expected, f"expected:\n{expected!r}\ngot:\n{result!r}"
    print("All clear-background tests passed.")
