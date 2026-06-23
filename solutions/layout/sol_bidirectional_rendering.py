"""Solution: Bidirectional Rendering — support left-to-right and right-to-left layout."""

from easy_mode import Block, Col, Row


class PlacedBlock(Block):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.x0 = None
        self.y0 = None

    def place(self, x0, y0):
        self.x0 = x0
        self.y0 = y0

    def report(self):
        return [
            "block",
            self.x0, self.y0,
            self.x0 + self.width, self.y0 + self.height,
        ]


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

    def report(self):
        return [
            "col",
            self.x0, self.y0,
            self.x0 + self.get_width(), self.y0 + self.get_height(),
        ] + [c.report() for c in self.children]


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

    def report(self):
        return [
            "row",
            self.x0, self.y0,
            self.x0 + self.get_width(), self.y0 + self.get_height(),
        ] + [c.report() for c in self.children]


class RTLPlacedRow(PlacedRow):
    """A row that places children from right to left."""

    def place(self, x0, y0):
        self.x0 = x0
        self.y0 = y0
        y1 = self.y0 + self.get_height()
        # Start from the right edge and work leftward.
        x_current = x0 + self.get_width()
        for child in self.children:
            child_y = y1 - child.get_height()
            x_current -= child.get_width()
            child.place(x_current, child_y)


def make_screen(width, height):
    return [[" "] * width for _ in range(height)]


def next_fill(fill):
    return "a" if fill is None else chr(ord(fill) + 1)


def draw(screen, node, fill=None):
    fill = next_fill(fill)
    for ix in range(node.get_width()):
        for iy in range(node.get_height()):
            screen[node.y0 + iy][node.x0 + ix] = fill
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
    # Left-to-right (default): Block(1,1) at x=0, Block(2,1) at x=1.
    ltr = PlacedRow(PlacedBlock(1, 1), PlacedBlock(2, 1))
    assert render(ltr) == "abb"

    # Right-to-left: Block(1,1) at x=2, Block(2,1) at x=0.
    rtl = RTLPlacedRow(PlacedBlock(1, 1), PlacedBlock(2, 1))
    assert render(rtl) == "bba"

    print("All bidirectional tests passed.")
