"""Solution: Equal Sizing — elastic columns that share row width equally."""

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


class EqualRow(PlacedRow):
    """A row that sizes its columns equally, distributing leftover space LTR."""

    def __init__(self, width, *children):
        super().__init__(*children)
        self._width = width

    def get_width(self):
        return self._width

    def get_height(self):
        return max((c.get_height() for c in self.children), default=0)

    def place(self, x0, y0):
        self.x0 = x0
        self.y0 = y0
        n = len(self.children)
        if n == 0:
            return
        base = self._width // n
        extra = self._width % n
        y1 = self.y0 + self.get_height()
        x_current = x0
        for i, child in enumerate(self.children):
            child_width = base + (1 if i < extra else 0)
            child._width = child_width
            child_y = y1 - child.get_height()
            child.place(x_current, child_y)
            x_current += child_width


class ElasticBlock(PlacedBlock):
    def __init__(self, height):
        super().__init__(0, height)

    def get_width(self):
        return self._width


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
    # Row width 10, 3 columns: base=3, extra=1 → widths [4, 3, 3].
    fixture = EqualRow(10, ElasticBlock(1), ElasticBlock(1), ElasticBlock(1))
    result = render(fixture)
    assert result == "aaaabbbccc", result

    # Row width 10, 4 columns: base=2, extra=2 → widths [3, 3, 2, 2].
    fixture = EqualRow(
        10, ElasticBlock(1), ElasticBlock(1), ElasticBlock(1), ElasticBlock(1)
    )
    result = render(fixture)
    assert result == "aaabbbccdd", result

    print("All equal-sizing tests passed.")
