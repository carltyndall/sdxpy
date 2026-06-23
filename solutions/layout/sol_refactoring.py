"""Solution: Refactoring — common parent class for blocks, rows, and columns."""


class Cell:
    """Common parent for all layout elements."""

    def get_width(self):
        raise NotImplementedError("subclasses must override get_width")

    def get_height(self):
        raise NotImplementedError("subclasses must override get_height")


class Block(Cell):
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height


class Row(Cell):
    def __init__(self, *children):
        self.children = list(children)

    def get_width(self):
        return sum(c.get_width() for c in self.children)

    def get_height(self):
        return max((c.get_height() for c in self.children), default=0)


class Col(Cell):
    def __init__(self, *children):
        self.children = list(children)

    def get_width(self):
        return max((c.get_width() for c in self.children), default=0)

    def get_height(self):
        return sum(c.get_height() for c in self.children)


if __name__ == "__main__":
    # Same tests as the original easy_mode tests, still pass.
    fixture = Block(1, 1)
    assert fixture.get_width() == 1
    assert fixture.get_height() == 1

    fixture = Row(Block(1, 1), Block(2, 4))
    assert fixture.get_width() == 3
    assert fixture.get_height() == 4

    fixture = Col(Block(1, 1), Block(2, 4))
    assert fixture.get_width() == 2
    assert fixture.get_height() == 5

    fixture = Col(
        Row(Block(1, 2), Block(3, 4)),
        Row(Block(5, 6), Col(Block(7, 8), Block(9, 10))),
    )
    assert fixture.get_width() == 14
    assert fixture.get_height() == 22

    print("All refactoring tests passed.")
