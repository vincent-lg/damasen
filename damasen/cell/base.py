"""Base cell."""

class Cell:

    """Base cell."""

    def __init__(self, y, x):
        self.y = y
        self.x = x

    @property
    def pos(self) -> tuple[int, int]:
        """Return the cell's position (y, x)."""
        return (self.y, self.x)
