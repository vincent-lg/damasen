"""Module containing the abstract tile type."""


class TileType:

    """Abstract tile type.

    All tile types should inherit from this class.

    """

    name: str
    display_character: str

    def display(self) -> str:
        """Display a tile on the map.

        This should return a single character. By default, simply return
        `display_character`.

        """
        return self.display_character
