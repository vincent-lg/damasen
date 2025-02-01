"""A tile object, representing a single tile on the map.

A tile does not contain cells (characters, vehicules, units...) or
clouds (smoke, fire, icy...). Instead, a tile has a type (wall, empty,
water, lava...). We separate both concepts, because a tile will not
be able to move on the map, but it could change type.

"""

from damasen.tile_type.base import TileType


class Tile:

    """A tile on the map.

    A tile has a type (empty, wall, water, lava...). Characters (cells)
    or clouds (smoke, fire...) are stored in the map itself, not on

    """

    def __init__(self, x: int, y: int, tile_type: TileType):
        self.x = x
        self.y = y
        self.type = tile_type

    def display(self) -> str:
        """Display the tile has a single character.

        By default, if it has a character on it, display it. Else,
        if it has a cloud, display it. Otherwise, just display the tile type.

        """
        tile = self.type.display()
        return tile
