"""Cell package, to define cells.

A cell is either a character or unit (hence the name). It moves on
the map. The player has a cell (see `damasen.cell.player.PlayerCell`).
Monsters have cells as well (see `damasen.cell.other.OtherCell`).

"""

from damasen.cell.other import OtherCell
from damasen.cell.player import PlayerCell

__all__ = ["OtherCell", "PlayerCell"]
