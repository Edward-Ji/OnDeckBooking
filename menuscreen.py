from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import CardTransition, Screen
from kivy.properties import BooleanProperty

from mainwidgets import HoverWidget, MainButton, MainPopup, SelectionPopup, MessagePopup

from guest import *


class ActivityToggleBehavior(ToggleButtonBehavior):

    last = []

    def on_state(self, instance, value):
        if value == "down":
            self.last.append(self)
        if len(self.last) > 2:
            self.last.pop(0)

    # allow regression when booking challenge activity
    @classmethod
    def undo(cls):
        cls.last[0].state = "down"
        # note the index is 0 next line because cls.last is updated last line
        cls.last[0].state = "normal"
        MessagePopup(message="Booking abandoned!").open()


class ActivityBlock(HoverWidget, ActivityToggleBehavior, BoxLayout, Activity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if Guest.get_booked("activities", self.day) == self.name:
            self.state = "down"
        self.bind(state=self.update)
        
    def on_hover_enter(self):
        if self.state == "normal":
            self.border_color = .45, .45, .45, 1
    
    def on_hover_leave(self):
        if self.state == "normal":
            self.border_color = 0, 0, 0, 0
    
    def on_state(self, instance, value):
        super().on_state(instance, value)
        # update graphics
        if self.state == "down":
            self.border_color = 1, .48, .15, 1
        else:
            self.border_color = 0, 0, 0, 0

    def _update(self, *args):
        # update activity booking database
        Guest.book_activity("activities", self.day, self.name)
        MessagePopup(message="Booking saved!").open()

    def update(self, instance, value):
        if value == "down":
            # allow regression when booking challenging activity
            if self.rating == "challenging":
                # ask when booking activity rated as challenging
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
        # instantiate all activity available on the day
        for rating, activity in Activity.on_day(day=day).items():
            # add day to instance for future update to database
            self.add_widget(ActivityBlock(name=activity.name,
                                          rating=activity.rating,
                                          desc=activity.desc,
                                          price=activity.price,
                                          day=day))


class ActivityPicker(MainPopup):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        kwargs["title"] = "Activities available for day " + str(day)
        super().__init__(**kwargs)
        self.content.add_widget(ActivityLayout(day=day))
        self.content.spacing = 10

    def dismiss(self, *largs, **kwargs):
        super().dismiss(*largs, **kwargs)
        # refresh calendar button to show booked activity
        self.refresh_ref.refresh()


"""
Below are meal booking widgets.
"""


class MealBlock(ToggleButtonBehavior, HoverWidget, BoxLayout, Meal):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if Guest.get_booked("meals", self.day) == self.name:
            self.state = "down"
        self.bind(state=self.update)

    def on_hover_enter(self):
        if self.state == "normal":
            self.border_color = .45, .45, .45, 1
        

    def on_hover_leave(self):
        if self.state == "normal":
            self.border_color = 0, 0, 0, 0

    def on_state(self, instance, value):
        # update graphics
        if self.state == "down":
            self.border_color = 1, .48, .15, 1
        else:
            self.border_color = 0, 0, 0, 0

    def update(self, instance, value):
        if value == "down":
            Guest.book_activity("meals", self.day, self.name)
            MessagePopup(message="Meal booking saved!").open()


class MealLayout(BoxLayout):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        super().__init__(**kwargs)
        for meal in Meal.load():
            self.add_widget(MealBlock(name=meal.name,
                                      desc=meal.desc,
                                      day=day))


class MealPicker(MainPopup):

    def __init__(self, **kwargs):
        day = kwargs.pop("day")
        kwargs["title"] = "Meals available for day " + str(day)
        super().__init__(**kwargs)
        self.content.add_widget(MealLayout(day=day))
        self.content.spacing = 10

    def dismiss(self, *largs, **kwargs):
        super().dismiss(*largs, **kwargs)
        self.refresh_ref.refresh()


"""
Below are basic blocks that build up the calendar in main menu
"""


class BookButton(MainButton):
    
    def on_hover_enter(self):
        pass
    
    def on_hover_leave(self):
        pass


class CalendarSubBlock(HoverWidget, RelativeLayout):
    
    unavailable = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.book_btn = BookButton()
        self.book_btn.bind(on_release=self.book)
    
    def on_hover_enter(self):
        self.add_widget(self.book_btn)
    
    def on_hover_leave(self):
        self.remove_widget(self.book_btn)
    
    def on_touch_up(self, touch):
        pass
    


class CalendarActivityBlock(CalendarSubBlock):
    
    def refresh(self):
        if self.day <= Activity.BOOK_AHEAD:
            self.name = "No activity available"
            self.unavailable = True
            if "image" in self.ids:
                self.remove_widget(self.ids.image)
        else:
            activity = Guest.get_booked("activities", self.day)
            if activity == Activity.no_activity().name:
                self.name = Activity.no_activity().name
            else:
                self.name = activity
            self.img = Activity.find(self.name).img
            if self.day < get_day() + Activity.BOOK_AHEAD:
                self.unavailable = True
            else:
                self.unavailable = False
    
    def book(self, *args):
        # handle unavailable situations
        if self.day <= Activity.BOOK_AHEAD:
            MessagePopup(message="There are no activities available for the first three days.").open()
        elif self.day < get_day():
            MessagePopup(message="You can not book activities for days before!").open()
        elif self.day < get_day() + Activity.BOOK_AHEAD:
            MessagePopup(message="You need to book activities at least three days ahead!").open()
        else:
            # initiate and open activity picker popup
            activity_picker = ActivityPicker(day=self.day)
            activity_picker.refresh_ref = self  # save for future update
            activity_picker.open()


class CalendarMealBlock(CalendarSubBlock):
    
    def refresh(self):
        self.name = Guest.get_booked("meals", self.day)
        self.img = Meal.find(self.name).img
        if self.day <= get_day():
            self.unavailable = True
        else:
            self.unavailable = False
    
    def book(self, *args):
        if self.day <= get_day():
            MessagePopup(message="You can not book meal for today or days before!").open()
        else:
            popup = MealPicker(day=self.day)
            popup.refresh_ref = self
            popup.open()


class CalendarBlock(BoxLayout):

    def __init__(self, **kwargs):
        day_count = kwargs.pop("day")
        super().__init__(**kwargs)
        self.day = day_count
        self.doc = " (Today)"

    def refresh(self):
        self.ids.activity_btn.refresh()
        self.ids.meal_btn.refresh()
        if self.day == get_day():
            self.doc = " (Today)"
        else:
            self.doc = ''


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
        # refresh the booking calendar every time screen appears
        self.ids.calendar.refresh()
        self.username = Guest.logged_in

    def logout(self):

        def _logout(*args):
            # change to login screen and logout
            self.manager.transition = CardTransition(direction="down", mode="push")
            self.manager.current = "login"
            Guest.logout()

        # warn about logging out first
        popup = SelectionPopup(title="Warning",
                               message="After logout you have to type in your credentials again.\n"
                                       "Do you really want to logout?")
        popup.add_choice(text="Logout",
                         on_release=_logout)
        popup.add_choice(text="Cancel")
        popup.open()

    def to_profile(self):  # go to profile screen with set animation
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "profile"
        self.manager.transition = CardTransition(direction="up", mode="pop")

    def to_cost(self):  # go to cost screen with set animation
        self.manager.transition = CardTransition(direction="down", mode="push")
        self.manager.current = "cost"
        self.manager.transition = CardTransition(direction="up", mode="pop")
