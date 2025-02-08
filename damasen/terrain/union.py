"""Union tile to allow several terrains."""

from damasen.terrain.base import Terrain


class Union:

    """Union of terrains."""

    def __init__(self, terrains: list[Terrain]):
        self.terrains = terrains

    def __repr__(self):
        return " | ".join([repr(terrain) for terrain in self.terrains])
