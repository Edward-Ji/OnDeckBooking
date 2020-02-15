from kivy.animation import Animation
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout

from guest import Guest
from mainwidgets import MainPopup


class LoginField(BoxLayout):

    @classmethod
    def login(cls, usr_input, psw_input):
        msg = Guest.login(usr_input.text, psw_input.text)
        if msg:  # login failed
            popup = MainPopup(title="Login failed!")
            popup.content.add_widget(Label(text=msg))
            popup.open()
            popup.close_btn.bind(on_release=lambda _: setattr(usr_input, "focus", True))
        else:
            root = App.get_running_app().root  # main screen manager
            root.current = "menu"


class AnimationLayout(RelativeLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CruiseImage(Image):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos = 150, 400
        animation = Animation(pos=(-175, 150), t="out_quad", duration=3)
        animation.start(self)
