"""Unknown tile (not visible)."""

from damasen.terrain.base import Terrain


class Unknown(Terrain):

    """Unknown tile."""

    display_character: str = " "
