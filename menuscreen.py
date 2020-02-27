from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import CardTransition, Screen
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.properties import BooleanProperty

from mainwidgets import MainLabel, MainButton, MainPopup, SelectionPopup, MessagePopup

from guest import *


class CalendarActivityButton(MainButton):
    unavailable = BooleanProperty(False)

    def refresh(self):
        if self.day <= 3:
            self.text = "No activity available"
            self.unavailable = True
        else:
            activity = Guest.get_booked(self.day)
            if activity == Activity.no_activity().name:
                self.text = "No activity booked"
            else:
                self.text = activity
            if self.day <= Activity.day() + 3:
                self.unavailable = True
            else:
                self.text += "\n[i][size=16]Tap to book[/size][/i]"

    def on_release(self):
        if self.day <= 3:
            MessagePopup(message="There are no activities available for the first three days.").open()
        elif self.day <= Activity.day() + 3:
            MessagePopup(message="You need to book activities at least three days ahead!").open()
        else:
            activity_picker = ActivityPicker(day=self.day,
                                             title="Activities available for day " + str(self.day))
            activity_picker.refresh_ref = self
            activity_picker.open()


class ActivityPickButton(MainButton, ToggleButtonBehavior):
    last = []

    def on_state(self, instance, value):
        if value == "down":
            ActivityPickButton.last.append(self)
        if len(ActivityPickButton.last) > 2:
            ActivityPickButton.last.pop(0)

    @classmethod
    def undo(cls):
        cls.last[0].state = "down"
        cls.last[0].state = "normal"
        MessagePopup(message="Booking abandoned!").open()


class ActivityBlock(BoxLayout, Activity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pick_btn = self.ids.pick_btn
        if Guest.get_booked(self.day) == self.name:
            pick_btn.state = "down"
        pick_btn.bind(state=self.update)

    def _update(self, *args):
        Guest.book_activity(self.day, self.name)
        MessagePopup(message="Booking saved!").open()

    def update(self, instance, value):
        if value == "down":
            if self.rating == "challenging":
                popup = SelectionPopup(title="Warning",
                                       message="Be aware that this activity is challenging.\n"
                                               "Please confirm that you have no disability or disease "
                                               "that could potentially cause harm to your body.")
                popup.add_choice(text="Book anyway",
                                 on_release=self._update)
                popup.add_choice(text="Cancel",
                                 on_release=lambda _: instance.undo())
                popup.open()
            else:
                self._update()


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


class CalendarMealButton(MainButton):
    unavailable = BooleanProperty(False)

    def refresh(self):
        self.text = "Default meal"  # todo: call get meal
        if self.day <= Activity.day():
            self.unavailable = True
        else:
            self.text += "\n[i][size=16]Tap to book[/size][/i]"

    def on_release(self):
        if self.day <= Activity.day():
            MessagePopup(message="You need to book meals at least one day ahead!").open()
        else:
            meal_picker = None  # todo: meal picker popup


class CalendarBlock(BoxLayout):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        self.day = day

    def refresh(self):
        self.ids.activity_btn.refresh()
        self.ids.meal_btn.refresh()
        if self.day == Activity.day():
            if not self.ids.day_label.text.endswith(" (Today)"):
                self.ids.day_label.text += " (Today)"
        else:
            if self.ids.day_label.text.endswith(" (Today)"):
                self.ids.day_label.text = self.ids.day_label.text[:-8]


class CalendarLayout(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for day in range(1, 15):
            self.add_widget(CalendarBlock(day=day))

    def refresh(self):
        for widget in self.children:
            widget.refresh()


class MenuScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids.calendar.refresh()

    def _logout(self, *args):
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "login"
        Guest.logout()

    def logout(self):
        popup = SelectionPopup(title="Warning",
                               message="After logout you have to type in your credentials again.\n"
                                       "Do you really want to logout?")
        popup.add_choice(text="Logout",
                         on_release=self._logout)
        popup.add_choice(text="Cancel")
        popup.open()

    def to_profile(self):
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "profile"
        self.manager.transition = CardTransition(direction="up", mode="pop")

    def to_cost(self):
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "cost"
        self.manager.transition = CardTransition(direction="up", mode="pop")
