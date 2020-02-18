from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from guest import *


class ReceiptLayout(BoxLayout):

    single = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ReceiptLayout.single = self

    def refresh(self):
        self.clear_widgets()
        receipt, total = Guest.costs()
        for activity in receipt:
            self.add_widget(Label(text="{} on day {}: ${}".format(activity.name,
                                                                  activity.day,
                                                                  activity.price),
                                  color=(0, 0, 0, 1)))
        self.add_widget(Label(text="Total: ${}".format(total),
                              color=(0, 0, 0, 1)))
