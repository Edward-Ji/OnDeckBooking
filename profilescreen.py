from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from mainwidgets import MainPopup, SelectionPopup, MessagePopup

from guest import *


class ProfileInput(BoxLayout):

    saved = StringProperty()

    @property
    def changed(self):
        return self.ids.input.text != self.saved

    def refresh(self):
        self.saved = str(Guest.get_profile(self.name.lower()))
        self.ids.input.text = self.saved

    def update(self):
        Guest.set_profile(self.name.lower(), self.ids.input.text)


class ProfilePassword(BoxLayout):

    @staticmethod
    def change_psw():
        popup = MainPopup(title="Change password")
        psw_change_layout = PasswordChangeLayout()
        psw_change_layout.popup = popup  # save reference to dismiss popup if needed
        popup.content.add_widget(psw_change_layout)
        popup.open()


class PasswordChangeLayout(AnchorLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.ori_psw_input.focus = True
        self.ids.ori_psw_input.text = '1'  # temporary solution to cursor disappearance bug
        self.ids.ori_psw_input.text = ''
        self.ids.new_psw_input.text = '1'
        self.ids.new_psw_input.text = ''

    def confirm(self):
        ori_psw_input = self.ids.ori_psw_input
        ori_psw = ori_psw_input.text
        new_psw = self.ids.new_psw_input.text
        msg = Guest.change_psw(ori_psw, new_psw)
        if msg:
            MessagePopup(message=msg).open()
            ori_psw_input.focus = True
        else:
            MessagePopup(message="Password changed successfully!").open()
            self.popup.dismiss()


class ProfileScreen(Screen):

    @property
    def changed(self):
        for widget in self.all_input:
            if widget.changed:
                return True

    @property
    def all_input(self):
        for widget in self.walk():
            if type(widget) == ProfileInput:
                yield widget

    def on_pre_enter(self, *args):
        for widget in self.all_input:
            widget.refresh()

    def update_profile(self):
        if self.changed:
            for widget in self.all_input:
                widget.update()
            MessagePopup(message="Changes saved!").open()
        self.manager.current = "menu"

    def to_menu(self):
        if self.changed:
            popup = SelectionPopup(title="Warning",
                                   message="You have unsaved changes.\n"
                                           "Do you want to go back to main menu without saving?")
            popup.add_choice("Don't save",
                             on_release=lambda _: setattr(self.manager, "current", "menu"))
            popup.add_choice("Save",
                             on_release=lambda _: setattr(self.manager, "current", "menu"))\
                .bind(on_release=lambda _: self.update_profile())
            popup.add_choice(text="Cancel")
            popup.open()
        else:
            self.manager.current = "menu"
