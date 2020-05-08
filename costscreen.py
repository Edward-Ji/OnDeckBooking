from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, NumericProperty

from mainwidgets import MainButton, MessagePopup, SelectionPopup

from guest import *


class ReceiptCancelButton(MainButton):
    
    unavailable = BooleanProperty()
    
    def on_release(self):
        if self.unavailable:
            MessagePopup(message="This activity has already finished!").open()
        else:
            self.parent.parent.cancel()


class ReceiptBlock(BoxLayout):

    def __init__(self, **kwargs):
        # initiate with given activity information
        self.name = kwargs.pop("name")
        self.day = kwargs.pop("day")
        self.price = kwargs.pop("price")
        self.finished = self.day < get_day() + Activity.BOOK_AHEAD
        super().__init__(**kwargs)
        
    def _cancel(self):
        Guest.book_activity("activities", self.day, Activity.no_activity().name)
        self.parent.remove_widget(self)
        MessagePopup(message="This activity is cancelled!")
        
    def cancel(self):
        popup = SelectionPopup(title="Warning",
                               message="After cancelling this activity, you'll have to rebook it in the main menu.\n"
                                       "Are you sure you want to cancel this event?")
        popup.add_choice(text="Cancel Activity",
                         on_release=lambda _: self._cancel())
        popup.add_choice(text="Do Not Cancel")
        popup.open()


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
                # instantiate rows using activity objects
                layout.add_widget(ReceiptBlock(name=activity.name,
                                               day=activity.day,
                                               price=activity.price))
        else:
            MessagePopup(message="You haven't booked any activity yet.").open()
        self.total = total


class CostScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids.receipt_layout.refresh()
