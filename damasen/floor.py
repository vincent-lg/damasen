"""Abstract floor definition.

Damasen is constituted of levels of difficulty. Each level might
contain one or more floors. A floor is just a suite of horizontal
coordinates. Templates are used to create a semi-random floor.

"""

import random

import numpy as np

from damasen.finder import compute_mst, dijkstra
from damasen.mixins.enhanced import EnhancedWithData
from damasen.template import Template
from damasen.terrain import Empty, Entrance, Union, Unknown, Wall
from damasen.terrain.base import Terrain


class Floor(EnhancedWithData):

    """Abstract floor, to be inherited by actual floors located in the game directory."""

    allow_no_python_file = False
    allow_no_data_file = True

    size: tuple[int, int]
    templates: list[Template]

    def __init__(self):
        self.map: np.ndarray = np.full(self.size, 0, dtype=np.int8)
        self.mapping = {0: Wall}
        self.reversed_mapping = {Wall: 0}
        self.floor_templates = []

    @property
    def empty_tile(self) -> int:
        """Return the used number for an empty tile."""
        return self.reversed_mapping[Empty]

    @property
    def wall_tile(self) -> int:
        """Return the used number for a wall tile."""
        return self.reversed_mapping[Wall]

    def build_from_templates(self):
        """Build the floor map using the loaded templates.

        This method should browse the templates and create a semi-random map
        floor using templates, respecting their limitations.

        """
        self.build_mapping()
        self.build_floor_templates()
        self.build_floor_map()

    def build_mapping(self) -> dict[int, Terrain]:
        """Build the mapping for this floor.

        The mapping is a dictionary of symbols common to all the floor
        templates. Therefore, it is necessary to browse the templates
        and build a static mapping with a number representing a terrain.
        For instance, 5 might refer to an empty tile. 18 might represent
        a forest.

        """
        for template in self.templates:
            for symbol, terrain in template.symbols.items():
                if terrain not in self.mapping.values():
                    index = max(self.mapping.keys(), default=-1) + 1

                    if index > 255:
                        raise ValueError("too many tiles to set in this floor")

                    self.mapping[index] = terrain
                    self.reversed_mapping[terrain] = index

    def build_floor_templates(self):
        """Build all the floor templates using the floor mapping.

        This requires to create a `np.ndarray` object per template,
        containing only the numbers relevant to each terrain.

        """
        self.floor_templates: list[tuple[np.ndarray, Template]] = []
        for template in self.templates:
            array = self.build_floor_template(template)
            self.floor_templates.append((array, template))

    def build_floor_template(self, template) -> np.ndarray:
        """Build a floor template for the given template.

        Args:
            template (Template): the template to use.

        Returns:
            array (np.ndarray): the map array using mapping numbers for terrain.

        """
        numbers = []
        terrains = {terrain: number for number, terrain in self.mapping.items()}

        for row in template.map.splitlines():
            num_row = []
            for character in row:
                # Find the number matching this type.
                terrain = template.symbols[character]
                number = terrains[terrain]
                num_row.append(number)
            numbers.append(num_row)

        return np.array(numbers, dtype=np.int8)

    def build_floor_map(self):
        """Build the floor map generated from the templates."""
        self.map: np.ndarray = np.full(self.size, 0, dtype=np.int8)
        terrains = {terrain: number for number, terrain in self.mapping.items()}
        empty = terrains[Empty]
        templates = self.get_floor_templates_to_use()
        occupied = np.zeros(self.size, dtype=bool)

        # Mark the edges as occupied, don't place anything there.
        occupied[0, :] = True
        occupied[-1, :] = True
        occupied[:, 0] = True
        occupied[:, -1] = True
        all_entrances = []

        # Try to place the templates
        for map, template in templates:
            windows = np.lib.stride_tricks.sliding_window_view(
                occupied, map.shape
            )
            valid_windows = ~np.any(windows, axis=(2, 3))
            valid_positions = np.argwhere(valid_windows)
            if valid_positions.shape[0] == 0:
                raise ValueError("no space to fit {template}")
            else:
                chosen_index = valid_positions[np.random.randint(len(valid_positions))]
                y, x = chosen_index
                t_height, t_width = map.shape
                entrances = self.place_template_entrances(
                    map, template, terrains
                )
                self.map[y:y + t_height, x:x + t_width] = map
                occupied[y:y + t_height, x:x + t_width] = True
                entrances = [(x + entrance[1], y + entrance[0]) for entrance in entrances]
                all_entrances.extend(entrances)

        # Compute MST for room connections
        connections = compute_mst(all_entrances)

        # Draw paths using `dijkstra`
        for start, end in connections:
            path = dijkstra(self.map, start, end)

            for x, y in path:
                self.map[y, x] = empty

    def get_floor_templates_to_use(self):
        """Return a list of floor templates to use depending on their constraints."""
        templates = []
        for map, template in self.floor_templates:
            more = random.randint(template.min_on_floor, template.max_on_floor)
            for _ in range(more):
                map = np.array(map)
                templates.append((map, template))

        templates.sort(key=lambda el: -el[1].min_on_floor)
        return templates

    def place_template_entrances(
        self, map: np.ndarray, template: Template, terrains: dict[Terrain, int]
    ) -> list[np.ndarray]:
        """Rerun the entrances in a given template.

        Adjust the map, so that non-required entrances are adjusted properly.

        """
        entrance = terrains[Entrance]
        entrances = list(np.argwhere(map == entrance))

        if not entrances:
            raise ValueError("there is no entrance on template {template}")

        # Limit the number of entrances, if needed replace by no_entrance tile.
        if len(entrances) < template.min_entrances:
            raise ValueError(
                f"there should be at least {temlate.min_entrances}, "
                f"but there are only {len(entrances)} entrances"
            )

        if len(entrances) > template.max_entrances:
            # Randomly choose entrances. Relace the other entrances
            # with the no_entrance tile.
            # Replace the other entrances by the no_entrance tile.
            no_entrance_tile = terrains[template.no_entrance_tile]
            to_remove = len(entrances) - template.max_entrances
            for _ in range(to_remove):
                index = random.randint(0, len(entrances) - 1)
                (y, x) = entrances.pop(index)
                map[y, x] = no_entrance_tile

        return entrances

    def print_map(self):
        """Print the whole map, for debugging purpose."""
        for row in self.map:
            for number in row:
                tile = self.mapping[number]
                print(tile.display_character, end="")
            print()

    @classmethod
    def load(cls, level: str, floor: str) -> "Floor":
        """Load a floor with its templates.

        Args:
            level (str): the unique name of the level.
            floor (str): the unique name of the floor to load.

        Returns:
            cls (Level): the loaded class level.

        """
        address = f"game/floors/{level}/{floor}"
        cls_level = cls.load_one(f"{address}.py", f"{address}.txt")

        # Load templates for this level.
        address = f"game/templates/{level}/{floor}"
        cls_level.templates = Template.load_all(address, address)

        return cls_level
