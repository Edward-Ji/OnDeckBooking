from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from mainwidgets import MainButton, MainPopup

from guest import *


class CalendarActivityButton(MainButton):

    def on_release(self):
        if self.day <= 3:
            popup = MainPopup(title="Sorry")
            popup.content.add_widget(Label(text="There are no activities available for the first three days."))
            popup.open()
        else:
            activity_picker = ActivityPicker(day=self.day,
                                             title="Activity booking for day "+str(self.day),
                                             size_hint=(.95, .95))
            activity_picker.open()


class CalendarBlock(BoxLayout):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        self.day = day


class CalendarLayout(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
                                          desc=activity.desc,
                                          price=activity.price,
                                          day=day))


class ActivityPicker(MainPopup):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        self.content.add_widget(ActivityLayout(day=day))
        self.content.spacing = 10
