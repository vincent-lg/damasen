"""Module containing the game window."""

import wx


class GameWindow(wx.Frame):
    def __init__(self, game):
        super().__init__(None)
        self.game = game

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
