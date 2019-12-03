import kivy
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from mainwidgets import *
from loginscreen import *

from guest import *

kivy.require("1.11.1")

# configure window size, color and icon
Window.clearcolor = 1, 1, 1, 1
Config.set("input", "mouse", "mouse,multitouch_on_demand")

Builder.load_file("mainwidgets.kv")
Builder.load_file("loginscreen.kv")


class KimberlyQuestApp(App):

    def build(self):
        self.title = "Kimberly Quest"


KimberlyQuestApp().run()
