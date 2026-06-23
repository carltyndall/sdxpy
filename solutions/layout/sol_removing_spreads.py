"""Solution: Removing Spreads — use lists instead of varargs and *-spreading."""


class Block:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


class Row:
    def __init__(self, children):
        self.children = list(children)

    def get_width(self):
        return sum([c.get_width() for c in self.children])

    def get_height(self):
        return max([c.get_height() for c in self.children], default=0)


class Col:
    def __init__(self, children):
        self.children = list(children)

    def get_width(self):
        return max([c.get_width() for c in self.children], default=0)

    def get_height(self):
        return sum([c.get_height() for c in self.children])


if __name__ == "__main__":
    fixture = Block(1, 1)
    assert fixture.get_width() == 1
    assert fixture.get_height() == 1

    fixture = Row([Block(1, 1), Block(2, 4)])
    assert fixture.get_width() == 3
    assert fixture.get_height() == 4

    fixture = Col([Block(1, 1), Block(2, 4)])
    assert fixture.get_width() == 2
    assert fixture.get_height() == 5

    fixture = Col([
        Row([Block(1, 2), Block(3, 4)]),
        Row([Block(5, 6), Col([Block(7, 8), Block(9, 10)])]),
    ])
    assert fixture.get_width() == 14
    assert fixture.get_height() == 22

    print("All remove-spreads tests passed.")
