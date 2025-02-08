"""Abstract template definition.

A template is just a portion of a floor. That's the "static" part
of a random floor.

"""

from typing import Type

from damasen.mixins.enhanced import EnhancedWithData
from damasen.terrain import Empty, Entrance, Union, Unknown, Wall
from damasen.terrain.base import Terrain

NUMERIC_OPTIONS = (
    "min_on_floor", "max_on_floor", "min_entrances", "max_entrances"
)
STANDARD_TERRAINS = {
    "empty": Empty,
    "entrance": Entrance,
    "unknown": Unknown,
    "wall": Wall,
}

STANDARD_SYMBOLS = {
    "#": Wall,
    ".": Empty,
    "+": Entrance,
    " ": Unknown,
}


class Template(EnhancedWithData):

    """Abstract template, to be inherited by actual templates."""

    allow_no_python_file = True
    allow_no_data_file = False

    map: str
    symbols: dict[str, Type[Terrain]]
    min_on_floor: int = 1
    max_on_floor: int | None = None
    min_entrances: int = 1
    max_entrances: int | None = 1
    no_entrance_tile = Wall

    @classmethod

    def extend_from_data(cls, data):
        """Extend a class with some data.

        For templates, the data is found in a text file which contains
        the template map. Optionally, it can also contain the definition
        of symbols.

        """
        # We assume everyting before a double new line (\n\n) is the map proper.
        if "\n\n" in data:
            cls.map, args = data.split("\n\n", 1)
        else:
            cls.map = data
            args = ""
        cls.map = cls.map.rstrip("\n")

        symbols = STANDARD_SYMBOLS.copy()
        for arg in args.splitlines():
            match arg.split(" "):
                case [option, value] if option in NUMERIC_OPTIONS:
                    setattr(cls, option, int(value))
                case [character, definition] if len(character) == 1:
                    if terrain := cls.get_terrain(definition):
                        symbols[character] = terrain
                    else:
                        raise ValueError(
                            f"{definition!r} isn't a valid terrain definition"
                        )
                case _ if arg.strip():
                    raise ValueError(
                        f"{arg!r} isn't valid configuration for a template"
                    )

        cls.symbols = symbols
        cls.check_symbols()

    @classmethod
    def get_terrain(cls, definition: str):
        """Try to get a terrain from a string definition.

        The terrain definition can be something like:
            wall
            wall | empty
            1.mine.huge_rock
            1.mine.huge_rock | 2.mountain.chasm

        In other words, some names are recognized automatically
        (empty, entrance, unknown, wall) becauuse they map
        to static terrains that are required everywhere. But there's
        an option to specify a terrain from a path (it will be dynamically
        loaded). In this case, it should be located in
        `game/terrains/{level}/{floor}`. See the examples provided in this folder.

        Simple unions also are supported with the pipe (|) symbol.
        wall | empty means "this tile will be replaced by a wall or
        an empty tile, randomly". It is not advised to use unions
        in a way that could possibly create impassible tiles. More than
        two terrains can be specified in a union and they can either
        be sstandard or extended terrains.

        """
        if "|" in definition:
            definitions = [part.strip() for part in definition.split("|")]
            terrains = [cls.get_terrain(part) for part in definitions]
            terrain = Union(terrains)
        elif StandardTerrain := STANDARD_TERRAINS.get(definition):
            terrain = StandardTerrain
        else:
            terrain = Terrain.load_one(f"game/terrains/{definition}", None)

        return terrain

    @classmethod
    def check_symbols(cls):
        """Check that all characters on the map have been defined as symbols."""
        for character in cls.map:
            if character == "\n":
                continue

            if character not in cls.symbols:
                raise ValueError(
                    f"there is no definition for the symbol {character!r}"
                )
