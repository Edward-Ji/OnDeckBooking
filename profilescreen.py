from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from mainwidgets import MainLabel, MainButton, MainPopup, MessagePopup

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

    def confirm(self):
        ori_psw_input = self.ids.ori_psw_input
        ori_psw = ori_psw_input.text
        new_psw = self.ids.new_psw_input.text
        msg = Guest.change_psw(ori_psw, new_psw)
        if msg:
            MessagePopup(message=msg).open()
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
            popup = MainPopup(title="Warning")
            popup.content.add_widget(MainLabel(text="You have unsaved changes.\n"
                                                    "Do you really want to quit without saving?"))
            menu_btn = MainButton(text="Quit",
                                  pos_hint={"center_x": .5})
            menu_btn.bind(on_release=lambda _: setattr(self.manager, "current", "menu"))
            menu_btn.bind(on_release=popup.dismiss)
            popup.content.add_widget(menu_btn)
            popup.open()
            popup.close_btn.text = "Cancel"
        else:
            self.manager.current = "menu"
