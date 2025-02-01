"""Class representing a map.

This is a horizontal construct (just with Xs and Ys) but it can span
an entire level. It contains tiles (see the `tile` module), cells
(see the `cell` package) and clouds (see the `cloud` package).

A map can describe itself for a given game at a given point, or location
(called focus). For instance, a map can contain an entire floor, but
the focus be in the northwest and the map would just display what
is around the focus in a given radius.

"""

from damasen.tile import Tile


class Map:

    """A map, a horizontal structure of tiles, cells and clouds."""

    def __init__(self, tiles: list[Tile]) -> None:
        self.tiles = {(tile.x, tile.y): tile for tile in tiles}
        self.cells = []
        self.clouds = []

    def display(self, focus: tuple[int, int], radius: int = 7) -> str:
        """Return the string describing the map around the focal point.

        Args:
            focus (tuple): the focus as a (x, y) tuple.
            radius (int): the radius to display around the focus.

        Returns:
            map (str): the represented map.

        """
        text = ""
        cells = {(cell.x, cell.y): cell for cell in self.cells}
        clouds = {(cloud.x, cloud.y): cloud for cloud in self.clouds}

        f_x, f_y = focus
        for y in range(f_y + radius, f_y - radius - 1, -1):
            if text:
                text += "\n"

            for x in range(f_x - radius, f_x + radius + 1):
                if cell := cells.get((x, y)):
                    text += cell.display()
                elif cloud := clouds.get((x, y)):
                    text += cloud.display()
                elif tile := self.tiles.get((x, y)):
                    text += tile.display()
                else:
                    text += " "

        return text
