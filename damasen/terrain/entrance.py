"""Entrance tile (entrance on a map template).."""

from damasen.terrain.base import Terrain


class Entrance(Terrain):

    """Entrance tile."""

    display_character: str = "+"
