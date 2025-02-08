"""Base terrain.

Each tile (coordinates on a map) has a reference to a terrain. This terrain
is the type of the tile (an empty tile, a wall, some water, some lava...).
Tiles do not account for characters or clouds as these are more dynamic.
A tile can change terrain if necessary.

"""

from damasen.mixins.enhanced import EnhancedWithData


class Terrain(EnhancedWithData):

    """Abstract terrain, to be inherited by actual terrains."""

    allow_no_python_file = False
    allow_no_data_file = True

    display_character: str
