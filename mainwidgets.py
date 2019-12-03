from kivy.uix.textinput import TextInput

import re


class MainInput(TextInput):

    def insert_text(self, substring, from_undo=False):
        if len(self.text) + len(substring) > self.allowed_len:
            substring = substring[:self.allowed_len - len(self.text)]
        if not re.match(self.allowed_pat, substring):
            substring = ''
        return super().insert_text(substring, from_undo=from_undo)
