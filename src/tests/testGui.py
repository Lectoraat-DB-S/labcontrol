import wx

class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Show(True)

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
#frame = wx.Frame(None, wx.ID_ANY, "LabControl Installer") # A Frame is a top-level window.
frame = MyFrame(None, 'Small editor')
#frame.Show(True)     # Show the frame.
app.MainLoop()