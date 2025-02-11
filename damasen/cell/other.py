"""Other cell (monster, allie, anything but the player)."""

from damasen.cell.base import Cell
from damasen.mixins.enhanced import EnhancedWithData


class OtherCell(EnhancedWithData, Cell):

    """Other cell, anything but the player."""

    allow_no_python_file = False
    allow_no_data_file = True

    display_character: str
