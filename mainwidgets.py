from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

import re


class MainLabel(Label):
    pass


class MainButton(Button):
    pass


class MainInput(TextInput):

    def insert_text(self, substring, from_undo=False):
        if len(self.text) + len(substring) > self.allowed_len:
            substring = substring[:self.allowed_len - len(self.text)]
        if not re.match(self.allowed_pat, substring):
            substring = ''
        return super().insert_text(substring, from_undo=from_undo)


class MainPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.content:
            self.add_widget(BoxLayout(orientation="vertical",
                                      spacing=5))
        self.close_btn = None

    def open(self, *largs, **kwargs):
        self.close_btn = MainButton(text="Close",
                                    font_size="18dp",
                                    pos_hint={"center_x": .5})
        self.close_btn.bind(on_release=self.dismiss)
        self.content.add_widget(self.close_btn)
        super().open(*largs, **kwargs)
