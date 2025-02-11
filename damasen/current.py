"""Module containing a class to keep track of the camera (current floor, cells, clouds...).

The Current object is definted once. It should always have a floor
(see `damasen.floor.Floor`). It can have a reference to the character cell
(a character or unit) and references to other cells (other characters
or units beyond the player). It can also refer to clouds. It maintains
the current view as a relative map of line-of-sight (usually what
the player will see).

"""

import numpy as np

from damasen.cell import OtherCell, PlayerCell
from damasen.cloud import Cloud
from damasen.finder import compute_fov
from damasen.floor import Floor


class Current:

    """Current object, describing a game view at a given point.

    Usually, ths view is updated, so old views are not accessible.

    The current object contains:
        player_cell: a reference to a Cell (a character or unit) to represent the player.
        floor_cells: a dict of Cell objects to represents cells in this floor.
        floor_clouds: a dict of Cloud objects active for this floor.
        view: a `np.ndarray` to represent the Line-Of-Sight map.

    """

    def __init__(
        self,
        floor: Floor,
        player_cell: PlayerCell | None = None,
        floor_cells: list[OtherCell] | None = None,
        floor_clouds: list[Cloud] | None = None,
    ) -> None:
        self.floor = floor
        self.player_cell = player_cell

        if floor_cells is not None:
            self.floor_cells = {cell.pos: cell for cell in floor_cells}
        else:
            self.floor_cells = {}

        if floor_clouds is not None:
            self.floor_clouds = {cloud.pos: cloud for cloud in floor_clouds}
        else:
            self.floor_clouds = {}

        self.display_map: str = ""
        self.display_mask = None
        self.los_mask = None
        self.memory = None

    def randomly_place_player_cell(self):
        """Randomly place the player cell on the map.

        This method is to be called once when no player cell has been defined yet.

        """
        if self.floor is None:
            raise ValueError("no floor map has been set yet")

        if self.player_cell is not None:
            raise ValueError("the player cell has already been placed.")

        empty = self.floor.empty_tile
        wall = self.floor.wall_tile
        wall_coords = np.argwhere(self.floor.map == wall)
        rows, cols = np.indices(self.floor.map.shape)
        all_coords = np.stack((rows, cols), axis=-1)

        # Reshape wall_coords to allow broadcasting
        wall_coords = wall_coords[:, None, None, :]
        all_coords = all_coords[None, :, :, :]

        # Compute (x1 - x2)^2 + (y1 - y2)^2 for each tile to each wall
        squared_distances = np.sum((all_coords - wall_coords) ** 2, axis=-1)
        min_squared_distances = np.min(squared_distances, axis=0)

        # Compute Euclidean distance
        distance_from_walls = np.sqrt(min_squared_distances)

        # Create the mask of valid tiles
        valid_tiles = (self.floor.map == empty) & (distance_from_walls >= 2)
        valid_indices = np.argwhere(valid_tiles)
        if valid_indices.size > 0:
            (y, x) = valid_indices[np.random.choice(len(valid_indices))]
            self.player_cell = PlayerCell(y, x)
            print(f"Optimal. Place @ on {y, x}")
        else:
            # Place on an empty tile.
            empty_coords = np.argwhere(self.floor.map == empty)
            (y, x) = empty_coords[np.random.choice(len(empty_coords))]
            self.player_cell = PlayerCell(y, x)
            print(f"Non-optimal. Place @ on {y, x}")

    def generate(self, all_seeing: bool = False):
        """Generate (or re-generate) the line-of-sight map."""
        if self.floor is None:
            raise ValueError("a floor map is needed")

        if self.display_mask is None:
            self.display_mask = np.zeros_like(self.floor.map, dtype=bool)

        if self.los_mask is None:
            self.los_mask = np.zeros_like(self.floor.map, dtype=bool)

        if self.memory is None:
            self.memory = np.full_like(self.floor.map, " ", dtype=str)

        # Create or adjust the display mask
        height, width = self.floor.map.shape
        player_y, player_x = self.player_cell.pos
        y_indices, x_indices = np.ogrid[:height, :width]
        self.display_mask[:] = (
            ((y_indices - player_y) ** 2 + (x_indices - player_x) ** 2)
            <= 14 ** 2
        )

        # Update the Line-Of-Sight mask.
        blocks = [self.floor.wall_tile]
        self.los_mask[:] = compute_fov(self.floor.map, player_x, player_y, 7, blocks)

        if all_seeing:
            self.los_mask[:] = np.ones(self.floor.map.shape, dtype=bool)

        self.update_visible_map()

    def update_visible_map(self):
        """Update the visible map.

        The visible map is centered on the player. It contains the LOS
        (usually 7 tiles around the player) and the remembered tiles
        (if any) in a greater radius.

        Note:
            This function should be called AFTER the map has been (re)generated.

        """
        coords = np.argwhere(self.display_mask)

        if coords.size > 0:
            min_y, min_x = coords.min(axis=0)
            max_y, max_x = coords.max(axis=0)
            visible_region = np.full(
                (max_y - min_y, max_x - min_x), " ", dtype=str
            )

            for y, x in coords:
                # These coordinates could be: visible in LOS (compute everything),
                # or memorized (just display what was last seen there)
                # or nothing at all.
                if self.los_mask[y, x]:
                    character = self.display_tile(y, x)
                    self.memory[y, x] = character
                else:
                    character = self.memory[y, x]

                visible_region[y - max_y, x - max_x] = character

            self.display_map = ""
            for row in visible_region:
                for character in row:
                    self.display_map += character
                self.display_map += "\n"
            self.display_map = self.display_map.rstrip("\n")
        else:
            self.display_map = ""

    def display_tile(self, y: int, x: int) -> str:
        """Return a one-character display string for this tile.

        Args:
            y (int): the Y axis for this tile.
            x (int): the X axis for this tile.

        Returns:
            display (str): a one-character display string for this tile.

        """
        if (y, x) == self.player_cell.pos:
            return "@"
        elif cell := self.floor_cells.get((y, x)):
            return cell.display_character
        elif cloud := self.floor_clouds.get((y, x)):
            return cloud.display_character
        else:
            number = self.floor.map[y, x]
            terrain = self.floor.mapping[number]
            return terrain.display_character

    def move_player(self, direction: int) -> bool:
        """Try to move the player in the specified direction.

        Args:
            direction (int): the direction.

        """
        y, x = self.player_cell.pos
        if coordinates := self.project_coords(y, x, direction):
            y, x = coordinates
            if self.floor.map[y, x] != self.floor.empty_tile:
                print(f"Cannot move in {y}.{x}: {self.floor.map[y, x]} != {self.floor.empty_tile}")
            else:
                self.player_cell.y, self.player_cell.x = y, x

    def project_coords(self, y: int, x: int, direction: int) -> tuple[int, int]:
        """Project the coordinates of a movement in the given direction."""
        match direction:
            case 0:
                coordinates = (y, x + 1)
            case 1:
                coordinates = (y + 1, x + 1)
            case 2:
                coordinates = (y + 1, x)
            case 3:
                coordinates = (y + 1, x - 1)
            case 4:
                coordinates = (y, x - 1)
            case 5:
                coordinates = (y - 1, x - 1)
            case 6:
                coordinates = (y - 1, x)
            case 7:
                coordinates = (y - 1, x + 1)
            case _:
                raise ValueError(f"invalid direction: {direction}")

        if (
            0 <= coordinates[0] < self.floor.map.shape[0]
            and 0 <= coordinates[1] < self.floor.map.shape[1]
        ):
            return coordinates

        return None
