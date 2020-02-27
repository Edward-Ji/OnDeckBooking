import kivy
kivy.require("1.11.1")

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window, WindowBase
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from mainwidgets import *
from loginscreen import *
from menuscreen import *
from costscreen import *
from profilescreen import *

from guest import *

# configure window size, color and icon
WINDOW_WIDTH_MIN = 1200
WINDOW_HEIGHT_MIN = 720
Window.size = WINDOW_WIDTH_MIN, WINDOW_HEIGHT_MIN
Config.set("kivy", "exit_on_escape", 0)
Config.set("input", "mouse", "mouse,multitouch_on_demand")

Factory.register("RoundedWidget", RoundedWidget)
from kivy.uix.behaviors import TouchRippleButtonBehavior
Factory.register("TouchRippleButtonBehavior", TouchRippleButtonBehavior)

Builder.load_file("mainwidgets.kv")
Builder.load_file("loginscreen.kv")
Builder.load_file("menuscreen.kv")
Builder.load_file("costscreen.kv")
Builder.load_file("profilescreen.kv")


def validate_window_size(*args):
    if Window.width <= WINDOW_WIDTH_MIN:
        Window.size = WINDOW_WIDTH_MIN, Window.height
    if Window.height <= WINDOW_HEIGHT_MIN:
        Window.size = Window.width, WINDOW_HEIGHT_MIN


Window.bind(on_resize=validate_window_size)


class MainScreenManager(ScreenManager):
    pass


class KimberleyQuestApp(App):

    def build(self):
        self.title = "Kimberley Quest"
        self.icon = "res/icon.png"


KimberleyQuestApp().run()
