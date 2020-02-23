from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty

from mainwidgets import MessagePopup

from guest import *


class ReceiptBlock(BoxLayout):

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.day = kwargs.pop("day")
        self.price = kwargs.pop("price")
        super().__init__(**kwargs)


class TotalBlock(BoxLayout):

    def __init__(self, **kwargs):
        self.total = kwargs.pop("total")
        super().__init__(**kwargs)


class ReceiptLayout(BoxLayout):

    single = None
    total = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ReceiptLayout.single = self

    def refresh(self):
        layout = self.ids.receipt_blocks
        layout.clear_widgets()
        receipt, total = Guest.costs()
        if receipt:
            for activity in receipt:
                layout.add_widget(ReceiptBlock(name=activity.name,
                                               day=activity.day,
                                               price=activity.price))
        else:
            MessagePopup(message="You haven't booked any activity yet.").open()
        self.total = total


class CostScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids.receipt_layout.refresh()
