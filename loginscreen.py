from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import CardTransition

from guest import Guest
from mainwidgets import MessagePopup


class LoginField(BoxLayout):

    def login(self):
        usr_input = self.ids.usr_input
        psw_input = self.ids.psw_input
        msg = Guest.login(usr_input.text, psw_input.text)
        if msg:
            MessagePopup(message=msg).open()
            usr_input.focus = True
        else:
            usr_input.text = ''
            psw_input.text = ''
            root = App.get_running_app().root  # main screen manager
            root.transition = CardTransition(direction="up", mode="pop")
            root.current = "menu"
            
    @staticmethod
    def register():
        root = App.get_running_app().root  # main screen manager
        root.transition = CardTransition(direction="up", mode="pop")
        root.current = "register"


class CruiseImage(Image):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.play()

    def play(self):
        self.pos = 150, 450
        animation = Animation(pos=(-200, 175), t="out_quad", duration=3)
        Clock.schedule_once(lambda _: animation.start(self), 1)
