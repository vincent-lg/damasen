"""Empty tile (with nothing on it)."""

from damasen.terrain.base import Terrain


class Empty(Terrain):

    """Empty tile."""

    display_character: str = "."
