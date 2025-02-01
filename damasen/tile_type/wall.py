"""Module containing the wall tile type."""

from damasen.tile_type.base import TileType


class Wall(TileType):

    """A blocking wall."""

    name: str = "wall"
    display_character: str = "#"
