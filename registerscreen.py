from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen

import re

from mainwidgets import MainInput, MessagePopup, SelectionPopup

from guest import *


patterns = {
    "First name": r"\w+$",
    "Last name": r"\w+$",
    "Password": r".{6,}",
    "Age": r"[1-9]\d{0,2}$",
    "Cabin No.": r"\d{1,3}$",
    "Address": r"[\w,. ]+",
    "Notes": r".*"
}


class RegisterInput(MainInput):
    
    bg_color_valid = (.4, .4, .4, 1)
    bg_color_invalid = (1, .27, .27, 1)
    
    @property
    def valid(self):
        return re.match(patterns[self.name], self.text)
    
    def check(self):
        if not self.text:
            return
        if not re.match(patterns[self.name], self.text):
            MessagePopup(message="Your {} is not valid!".format(self.name.lower())).open()
            self.background_color = self.bg_color_invalid
        else:
            self.background_color = self.bg_color_valid
 
    def on_focus(self, instance, value):
        if not value:
            self.check()
        else:
            self.background_color = self.bg_color_valid


class RegisterInputField(BoxLayout):

    @property
    def value(self):
        return self.ids.input.text


class RegisterRadioField(BoxLayout):
    
    @property
    def value(self):
        for radio_btn in CheckBox.get_widgets(self.name):
            if radio_btn.state == "down":
                return radio_btn.value


class RegisterPasswordField(BoxLayout):
    
    @property
    def value(self):
        return self.ids.input.text


class RegisterScreen(Screen):
    
    @property
    def all_input(self):
        # walk through all profile input boxes
        for widget in self.walk():
            if type(widget) in (RegisterInputField, RegisterPasswordField, RegisterRadioField):
                yield widget

    def register(self):
        details = []
        for widget in self.all_input:
            if type(widget) in (RegisterInputField, RegisterPasswordField):
                if not widget.ids.input.valid:
                    MessagePopup(message="Your {} is not valid!".format(widget.name.lower())).open()
                    return
            details.append(widget.value)
        Guest.register(*details)
        self.manager.current = "login"
        MessagePopup(message="Successfully registered! Please login to continue.").open()
    
    def to_menu(self):
        # warn before leave
        popup = SelectionPopup(title="Warning",
                               message="You have not yet registered.\n"
                                       "Do you want to return to login screen without registering?\n")
        popup.add_choice("Leave", on_release=lambda _: setattr(self.manager, "current", "login"))
        popup.add_choice(text="Cancel")
        popup.open()
