from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import CardTransition, Screen
from kivy.uix.togglebutton import ToggleButtonBehavior

from mainwidgets import MainButton, MainPopup, SelectionPopup, MessagePopup

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
                self.text = activity
            self.text += "\n[i][size=16]Tap to book[/size][/i]"

    def on_release(self):
        if self.day <= 3:
            MessagePopup(message="There are no activities available for the first three days.").open()
        else:
            activity_picker = ActivityPicker(day=self.day,
                                             title="Activities available for day "+str(self.day))
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


class ActivityPickButton(MainButton, ToggleButtonBehavior):

    def no_activity_down(self):
        all_btn = ToggleButtonBehavior.get_widgets(self.group)
        for btn in all_btn:
            if btn.name == Activity.no_activity().name:
                btn.state = "down"
        self.state = "normal"
        del all_btn  # necessary for garbage collecting


class ActivityBlock(BoxLayout, Activity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if Guest.get_booked(self.day) != self.name:
            self.ids.pick_btn.state = "normal"

    def _update(self, *args):
        Guest.book_activity(self.day, self.name)
        MessagePopup(message="Bookings saved!").open()

    def update(self):
        if self.ids.pick_btn.state == "down":
            if self.rating == "challenging":
                popup = SelectionPopup(title="Warning",
                                       message="Be aware that this activity is challenging.\n"
                                               "Please confirm that you have no disability or disease "
                                               "that could potentially cause harm to your body.")
                popup.add_choice(text="Book anyway",
                                 on_release=self._update)
                popup.add_choice(text="Cancel",
                                 on_release=lambda _: self.ids.pick_btn.no_activity_down())
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
