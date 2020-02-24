import kivy
kivy.require("1.11.1")

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from mainwidgets import *
from loginscreen import *
from menuscreen import *
from costscreen import *
from profilescreen import *

from guest import *

# configure window size, color and icon
Window.size = 1200, 740
Config.set("kivy", "exit_on_escape", 0)
Config.set("input", "mouse", "mouse,multitouch_on_demand")

Builder.load_file("mainwidgets.kv")
Builder.load_file("loginscreen.kv")
Builder.load_file("menuscreen.kv")
Builder.load_file("costscreen.kv")
Builder.load_file("profilescreen.kv")


class MainScreenManager(ScreenManager):
    pass


class KimberleyQuestApp(App):

    def build(self):
        self.title = "Kimberley Quest"
        self.icon = "res/icon.png"


KimberleyQuestApp().run()
