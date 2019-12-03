from kivy.uix.boxlayout import BoxLayout

from guest import Guest


class LoginField(BoxLayout):

    logged_in = None

    @classmethod
    def login(cls, usr_input, psw_input):
        # usr_input.disabled = True
        # psw_input.disabled = True
        msg = Guest.login(usr_input.text, psw_input.text)
        if msg:
            print(msg)
        else:
            print("logged in")
        # usr_input.disabled = False
        # psw_input.disabled = False
