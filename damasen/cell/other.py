"""Other cell (monster, allie, anything but the player)."""

from damasen.cell.base import Cell
from damasen.mixins.enhanced import EnhancedWithData


class OtherCell(EnhancedWithData, Cell):

    """Other cell, anything but the player."""

    allow_no_python_file = True
    allow_no_data_file = True
    specifications = {
        "display_char": "any",
        "range": "interval",
    }

    display_character: str
    range: tuple[int, int]
