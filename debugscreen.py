from kivy.uix.boxlayout import BoxLayout
from mainwidgets import MainButton, MessagePopup

from datetime import datetime, timedelta
from tinydb import TinyDB, Query

MANAGER_FILE = "_manager.py"


class ResetDatabaseButton(MainButton):

    def on_release(self):
        with open(self.name + MANAGER_FILE) as f:
            code = ''.join(f.readlines())
            MessagePopup(message="resetting " + self.name + " database").open()
            exec(code)
            MessagePopup(message=self.name + " database successfully reset").open()


class SetDayInput(BoxLayout):

    def confirm(self):
        guest_db = TinyDB("guest.json")
        query = Query()
        day = int(self.ids.day_input.text)
        if day < 1 or day > 14:
            MessagePopup(message="day must be between 1 and 14 (boundary inclusive)").open()
        start_date = datetime.now() - timedelta(days=day-1)
        guest_db.update({"start": start_date.strftime("%d%m%y")}, query.journey == "Kimberley Quest")
        MessagePopup(message="successfully updated start date to " + start_date.strftime("%d/%m/%y")).open()
