"""Solution: Clipping Text — clip text that is too wide, and optionally break on spaces."""


class TextBlock:
    """A block with actual text content rather than a character fill."""

    def __init__(self, text, width=None):
        self.text = text
        self._width = width if width is not None else len(text)

    def get_width(self):
        return self._width

    def get_height(self):
        return 1


def clip_text(text, width):
    """Return text truncated to at most `width` characters."""
    return text[:width]


def break_on_spaces(text, width):
    """Break `text` on spaces so that no line exceeds `width`; clip otherwise."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        if len(word) > width:
            if current:
                lines.append(current.rstrip())
                current = ""
            lines.append(word[:width])
        elif current and len(current) + 1 + len(word) > width:
            lines.append(current.rstrip())
            current = word
        else:
            current = f"{current} {word}".lstrip()
    if current:
        lines.append(current)
    return lines


def render_block(block, width, height):
    """Produce a list of strings showing what would be rendered for a block."""
    screen = [[" "] * width for _ in range(height)]
    text = clip_text(block.text, block.get_width())
    for i, ch in enumerate(text):
        if i < width:
            screen[0][i] = ch
    return ["".join(row) for row in screen]


if __name__ == "__main__":
    # Part 1: simple clipping.
    block = TextBlock("unfittable", width=5)
    assert clip_text(block.text, block.get_width()) == "unfit"

    # Part 2: break on spaces.
    text = "hello wonderful world of layout"
    lines = break_on_spaces(text, 10)
    assert lines == ["hello", "wonderful", "world of", "layout"], lines

    # Edge case: single long word gets clipped.
    assert break_on_spaces("supercalifragilistic", 6) == ["superc"]

    # Edge case: exact fit.
    assert break_on_spaces("hello world", 11) == ["hello world"]

    print("All clipping tests passed.")
