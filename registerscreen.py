from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen, CardTransition

import re

from mainwidgets import MainInput, MessagePopup, SelectionPopup

from guest import *


patterns = {
    "First name": r"[A-Za-z]+$",
    "Last name": r"[A-Za-z]+$",
    "Username": r"\S+$",
    "Password": r".{6,}",
    "Age": r"[1-9]\d{0,2}$",
    "Cabin No.": r"\d{1,3}$",
    "Address": r"[\w,. ]+",
    "Notes": r".*"
}

error_msg = {
    "First name": "First name can only contain letters!",
    "Last name": "First name can only contain letters!",
    "Username": "Username can not contain white spaces!",
    "Password": "Password must contain at least 6 characters!",
    "Age": "Age must be an integer no more than three digits!",
    "Cabin No.": "Cabin number must be a 1-to-3-digit number!",
    "Address": "Address is required and can not contain special characters!",
    "Notes": ''
}


class RegisterInput(MainInput):
    
    bg_color_valid = (.4, .4, .4, 1)
    bg_color_invalid = (1, .27, .27, 1)
    
    @property
    def error(self):
        if not re.match(patterns[self.name], self.text):
            return error_msg[self.name]
    
    def check(self):
        if not self.text:
            return
        msg = self.error
        if msg:
            MessagePopup(message=msg).open()
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
    def error(self):
        return self.ids.input.error

    @property
    def value(self):
        return self.ids.input.text
    
    def reset(self):
        self.ids.input.text = ''


class RegisterRadioField(BoxLayout):
    
    @property
    def error(self):
        for radio_btn in CheckBox.get_widgets(self.name):
            if radio_btn.state == "down":
                return
        else:
            return "You need to select your gender!"
    
    @property
    def value(self):
        for radio_btn in CheckBox.get_widgets(self.name):
            if radio_btn.state == "down":
                return radio_btn.value
            
    def reset(self):
        for radio_btn in CheckBox.get_widgets(self.name):
            radio_btn.state = "normal"


class RegisterUsernameField(BoxLayout):
    
    @property
    def error(self):
        msg = self.ids.input.error
        if msg:
            return msg
        if Guest.find(self.ids.input.text):  # check if username exits
            return "Sorry, the username has been taken!"
    
    @property
    def value(self):
        return self.ids.input.text
    
    def reset(self):
        self.ids.input.text = ''


class RegisterPasswordField(BoxLayout):
    
    @property
    def error(self):
        return self.ids.input.error
    
    @property
    def value(self):
        return self.ids.input.text
    
    def reset(self):
        self.ids.input.text = ''


class RegisterScreen(Screen):
    
    @property
    def all_input(self):
        # walk through all profile input boxes
        for widget in self.walk():
            if type(widget) in (RegisterInputField, RegisterUsernameField, RegisterPasswordField, RegisterRadioField):
                yield widget

    def register(self):
        details = []
        for widget in self.all_input:
            msg = widget.error
            if msg:
                MessagePopup(message=msg).open()
                return
            details.append(widget.value)
        Guest.register(*details)
        self._to_login()
        MessagePopup(message="Successfully registered! Please login to continue.").open()

    def _to_login(self, *args):
        # clear all field for privacy
        for widget in self.all_input:
            widget.reset()
    
        # change to login screen
        self.manager.transition = CardTransition(direction="down", mode="pop")
        self.manager.current = "login"
    
    def to_login(self):
        
        # warn before leave
        popup = SelectionPopup(title="Warning",
                               message="You have not yet registered.\n"
                                       "Do you want to return to login screen without registering?\n")
        popup.add_choice("Leave", on_release=self._to_login)
        popup.add_choice(text="Cancel")
        popup.open()
