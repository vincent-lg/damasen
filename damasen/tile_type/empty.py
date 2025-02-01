"""Module containing the empty tile type."""

from damasen.tile_type.base import TileType


class Empty(TileType):

    """An empty tile type with nothing on it."""

    name: str = "empty"
    display_character: str = "."
