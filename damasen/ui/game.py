"""Module containing the game window."""

import wx

from damasen.current import Current
from damasen.floor import Floor


DIRECTIONS = {
    wx.WXK_RIGHT: 0,
    "n": 1,
    wx.WXK_DOWN: 2,
    "b": 3,
    wx.WXK_LEFT: 4,
    "y": 5,
    wx.WXK_UP: 6,
    "u": 7,
}


class GameWindow(wx.Frame):
    def __init__(self, game):
        super().__init__(None)
        self.game = game
        cls_floor = Floor.load("1", "mine")
        self.floor = cls_floor()
        self.floor.build_from_templates()
        self.current = Current(self.floor)
        self.current.randomly_place_player_cell()

        self.SetTitle("Damasen")
        self.SetSize((600, 400))

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP
        self.map = wx.TextCtrl(panel, size=(400, 400), style=style)

        # Font
        size = 12
        # modern is a monotype font
        family = wx.FONTFAMILY_MODERN
        font = wx.Font(size, family, wx.NORMAL, wx.NORMAL)
        self.map.SetFont(font)
        vbox.Add(self.map, flag=wx.ALIGN_CENTER | wx.TOP, border=5)

        self.history = wx.ListCtrl(
            panel, size=(150, 150), style=wx.LC_REPORT | wx.LC_SINGLE_SEL
        )
        self.history.InsertColumn(0, "Messages")
        vbox.Add(self.history, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=5)

        panel.SetSizer(vbox)

        self.map.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.UpdateMap()

    def OnKeyDown(self, event):
        key_code = event.GetUnicodeKey() or event.GetKeyCode()
        modifiers = event.GetModifiers()

        if modifiers == 0:
            direction = None
            if (direction := DIRECTIONS.get(key_code)) is not None:
                self.current.move_player(direction)
                self.UpdateMap()
            elif 0 < key_code < 256:
                name = chr(key_code).lower()
                if (direction := DIRECTIONS.get(name)) is not None:
                    self.current.move_player(direction)
                    self.UpdateMap()

    def UpdateMap(self):
        """Update the map to be displayed."""
        self.current.generate()
        self.map.SetValue(self.current.display_map)
        y, x = self.current.relative_player_cell
        absolute_pos = self.map.XYToPosition(x, y)

        if absolute_pos != wx.NOT_FOUND:
            self.map.SetInsertionPoint(absolute_pos)
