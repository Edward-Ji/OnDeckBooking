from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ReceiptLayout.single = self

    def refresh(self):
        self.ids.receipt_blocks.clear_widgets()
        receipt, total = Guest.costs()
        for activity in receipt:
            self.ids.receipt_blocks.add_widget(ReceiptBlock(name=activity.name,
                                                            day=activity.day,
                                                            price=activity.price))
        self.add_widget(TotalBlock(total=total))


class CostScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids.receipt_layout.refresh()
