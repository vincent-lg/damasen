"""Script containing the main window."""

import wx

from damasen.ui.game import GameWindow


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SetTitle("Damasen")
        self.SetSize((300, 150))

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        play = wx.Button(panel, label="Play")
        play.Bind(wx.EVT_BUTTON, self.on_play)
        vbox.Add(play, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        quit = wx.Button(panel, label="Quit")
        quit.Bind(wx.EVT_BUTTON, self.on_quit)
        vbox.Add(quit, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def on_play(self, _event):
        game_window = GameWindow(None)
        game_window.Show()
        self.Destroy()

    def on_quit(self, _event):
        self.Close()

def main():
    app = wx.App(False)
    window = MainWindow(None)
    window.Show()
    app.MainLoop()
