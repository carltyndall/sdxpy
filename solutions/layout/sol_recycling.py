"""Solution: Recycling — only create new rows and columns for wrapping when needed."""

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

    def wrap(self):
        return self


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

    def wrap(self):
        return PlacedCol(*[c.wrap() for c in self.children])


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

    def _children_total_width(self, children):
        return sum(c.get_width() for c in children)

    def wrap(self):
        children = [c.wrap() for c in self.children]
        if self._children_total_width(children) <= self.get_width():
            return PlacedRow(*children)

        rows = self._bucket(children)
        new_rows = [PlacedRow(*r) for r in rows]
        new_col = PlacedCol(*new_rows)
        return PlacedRow(new_col)

    def _bucket(self, children):
        result = []
        current_row = []
        current_x = 0
        for child in children:
            child_width = child.get_width()
            if (current_x + child_width) <= self.get_width():
                current_row.append(child)
                current_x += child_width
            else:
                result.append(current_row)
                current_row = [child]
                current_x = child_width
        result.append(current_row)
        return result


class RecyclingRow(PlacedRow):
    def __init__(self, width, *children):
        super().__init__(*children)
        self._width = width

    def get_width(self):
        return self._width


class RecyclingBlock(PlacedBlock):
    pass


class RecyclingCol(PlacedCol):
    pass


if __name__ == "__main__":
    # Case 1: everything fits — no extra row/col inserted.
    fixture = RecyclingRow(10, RecyclingBlock(4, 1))
    wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert wrapped.report() == ["row", 0, 0, 4, 1, ["block", 0, 0, 4, 1]]

    # Case 2: doesn't fit — wrapping still works.
    fixture = RecyclingRow(3, RecyclingBlock(2, 1), RecyclingBlock(2, 1))
    wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert wrapped.report() == [
        "row",
        0, 0, 2, 2,
        [
            "col",
            0, 0, 2, 2,
            ["row", 0, 0, 2, 1, ["block", 0, 0, 2, 1]],
            ["row", 0, 1, 2, 2, ["block", 0, 1, 2, 2]],
        ],
    ]

    print("All recycling tests passed.")
