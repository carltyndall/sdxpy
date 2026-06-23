"""Solution: Properties — replace get_width/get_height with @property."""


class Block:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class Row:
    def __init__(self, *children):
        self.children = list(children)

    @property
    def width(self):
        return sum(c.width for c in self.children)

    @property
    def height(self):
        return max((c.height for c in self.children), default=0)


class Col:
    def __init__(self, *children):
        self.children = list(children)

    @property
    def width(self):
        return max((c.width for c in self.children), default=0)

    @property
    def height(self):
        return sum(c.height for c in self.children)


if __name__ == "__main__":
    fixture = Block(1, 1)
    assert fixture.width == 1
    assert fixture.height == 1

    fixture = Block(3, 4)
    assert fixture.width == 3
    assert fixture.height == 4

    fixture = Row(Block(1, 1), Block(2, 4))
    assert fixture.width == 3
    assert fixture.height == 4

    fixture = Col(Block(1, 1), Block(2, 4))
    assert fixture.width == 2
    assert fixture.height == 5

    fixture = Col(
        Row(Block(1, 2), Block(3, 4)),
        Row(Block(5, 6), Col(Block(7, 8), Block(9, 10))),
    )
    assert fixture.width == 14
    assert fixture.height == 22

    # Verify they are read-only properties (no setter).
    b = Block(2, 3)
    try:
        b.width = 99
    except AttributeError:
        pass
    else:
        raise AssertionError("width should be read-only")
    assert b.width == 2

    print("All property tests passed.")
