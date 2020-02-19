from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import CardTransition, Screen

from mainwidgets import MainButton, MainPopup
from costscreen import ReceiptLayout

from guest import *


class CalendarActivityButton(MainButton):

    def refresh(self):
        if self.day <= 3:
            self.text = "No activity available"
        else:
            activity = Guest.get_booked(self.day)
            if activity == Activity.no_activity().name:
                self.text = "No activity booked"
            else:
                self.text = "Booked:\n" + activity
            self.text += "\n[i][size=16]Tap to book activity[/size][/i]"

    def on_release(self):
        if self.day <= 3:
            popup = MainPopup(title="Sorry")
            popup.content.add_widget(Label(text="There are no activities available for the first three days."))
            popup.open()
        else:
            activity_picker = ActivityPicker(day=self.day,
                                             title="Activity booking for day "+str(self.day))
            activity_picker.refresh_ref = self
            activity_picker.open()


class CalendarBlock(BoxLayout):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        self.day = day
        self.ids.activity_btn.refresh()


class CalendarLayout(GridLayout):

    def refresh(self):
        self.clear_widgets()
        for day in range(1, 15):
            self.add_widget(CalendarBlock(day=day))


class ActivityBlock(BoxLayout, Activity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if Guest.get_booked(self.day) == self.name:
            self.pick_btn.state = "down"

    def update(self, state):
        if state == "down":
            Guest.book_activity(self.day, self.name)


class ActivityLayout(BoxLayout):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        for rating, activity in Activity.on_day(day=day).items():
            self.add_widget(ActivityBlock(name=activity.name,
                                          rating=activity.rating,
                                          desc=activity.desc,
                                          price=activity.price,
                                          day=day))


class ActivityPicker(MainPopup):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        self.content.add_widget(ActivityLayout(day=day))
        self.content.spacing = 10

    def dismiss(self, *largs, **kwargs):
        super().dismiss(*largs, **kwargs)
        self.refresh_ref.refresh()


class MenuScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids.calendar.refresh()

    def logout(self):
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "login"
        Guest.logout()

    def to_profile(self):
        self.manager.transition = CardTransition(direction="down", mode="push")
        # self.manager.current = "profile"
        self.manager.transition = CardTransition(direction="up", mode="pop")

    def to_cost(self):
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "cost"
        self.manager.transition = CardTransition(direction="up", mode="pop")
