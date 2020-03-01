from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, StringProperty

import re

RAPID_CLICK = .35


# logo image also serves as entry to debug screen
class LogoImage(Image):

    press_count = 0
    reset = None

    # activate debugging mode when logo is rapidly pressed
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.press_count += 1
            if self.reset:
                self.reset.cancel()
            self.reset = Clock.schedule_once(lambda _: setattr(self, "press_count", 0), RAPID_CLICK)
            if 7 <= self.press_count <= 9:
                MessagePopup(message="Tap {} more time(s) to debug mode!".format(10 - self.press_count)).open()
            elif self.press_count == 10:
                MessagePopup(message="You are now in debug mode!").open()
                App.get_running_app().root.current = "debug"


# provoke event upon the start and end of mouse hovering
class HoverBehavior(Widget):

    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.register_event_type('on_hover_enter')
        self.register_event_type('on_hover_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    # walk widget tree to check widget is inside a modal view
    @property
    def inside_modal_view(self):
        parent = self.parent
        while parent and not isinstance(parent, Screen):
            if isinstance(parent, ModalView):
                return True
            parent = parent.parent

    def on_mouse_pos(self, *args):
        if isinstance(App.get_running_app().root_window.children[0], Popup)\
                and not self.inside_modal_view:
            # do not provoke event when a popup is on display unless widget is in the popup
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            return
        self.hovered = inside
        if inside:
            self.dispatch('on_hover_enter')
        else:
            self.dispatch('on_hover_leave')

    # provoked when mouse enters area over widget
    def on_hover_enter(self):
        pass

    # provoked when mouse leaves area over widget
    def on_hover_leave(self):
        pass


# handle widget as rounded during collision event
class RoundedBehavior(Widget):

    def collide_point(self, *pos):
        if self.width != self.height:
            return super().collide_widget(*pos)
        radius = self.width / 2
        x, y = pos
        distance = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5
        return distance <= radius


# styled label
class MainLabel(Label):
    pass


# styled button
class MainButton(HoverBehavior, Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mask = None

    def on_hover_enter(self):
        # lighten the button upon mouse hover event
        with self.canvas:
            Color(rgba=(1, 1, 1, .08))
            self.mask = Rectangle(size=self.size,
                                  pos=self.pos)

    def on_hover_leave(self):
        # restore button when mouse hover event ends
        self.canvas.remove(self.mask)


# button displayed in the top bar
class HeadingButton(RoundedBehavior, HoverBehavior, Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hint = None

    def on_hover_enter(self):
        # show function of button when mouse hovers
        self.hint = Label(text=self.name.title(),
                          center=(self.center_x, self.y - 6))
        self.add_widget(self.hint)

    def on_hover_leave(self):
        # restore button when mouse leaves
        self.remove_widget(self.hint)


class MainInput(TextInput):

    def insert_text(self, substring, from_undo=False):
        # restrict input length to allowed length
        if len(self.text) + len(substring) > self.allowed_len:
            substring = substring[:self.allowed_len - len(self.text)]
        # restrict input to allowed pattern
        if not re.match(self.allowed_pat, substring):
            substring = ''
        return super().insert_text(substring, from_undo=from_undo)


# toggle show and hide password in input box
class PasswordEye(ToggleButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule_hide = None

    def on_state(self, instance, value):
        # automatically hide password two seconds after showing password
        if self.state == "down":
            if self.schedule_hide:
                self.schedule_hide.cancel()
            self.schedule_hide = Clock.schedule_once(lambda _: setattr(self, "state", "normal"), 2)


# styled popup
class MainPopup(Popup):
    pass


# selection popup with automated addition of option buttons
class SelectionPopup(Popup):

    message = StringProperty()

    def __init__(self, **kwargs):
        if "message" in kwargs:
            self.message = kwargs.pop("message")
        super().__init__(**kwargs)

    # automatically add option button to choice box and bind it with given event
    def add_choice(self, text, release_dismiss=True, **kwargs):
        choice_btn = MainButton(text=text)
        self.ids.choice_box.add_widget(choice_btn)
        choice_btn.bind(**kwargs)
        if release_dismiss:
            choice_btn.bind(on_release=self.dismiss)
        return choice_btn


# popup label with message that fades
class MessagePopup(ModalView):

    current = None

    def __init__(self, **kwargs):
        if MessagePopup.current:  # only display one at a time
            MessagePopup.current.opacity = 0
            MessagePopup.current.dismiss()
        MessagePopup.current = self
        self.message = kwargs.pop("message")
        self.fade = None
        self.dismiss_schedule = None
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        pass

    def on_touch_move(self, touch):
        pass

    def on_touch_up(self, touch):
        pass

    def open(self, *largs, **kwargs):
        super().open(*largs, **kwargs)
        # schedule fading animation
        self.dismiss_schedule = Clock.schedule_once(self.close, 1.6)

    def close(self, *args):
        # start fading animation
        self.fade = Animation(opacity=0, t="in_sine", duration=0.6)
        self.fade.start(self)
        # fully dismiss popup after animation
        self.dismiss_schedule = Clock.schedule_once(self.dismiss, 0.6)

    def dismiss(self, *largs, **kwargs):
        super().dismiss(*largs, **kwargs)
        if self.fade:
            self.fade.cancel(self)
        if self.dismiss_schedule:
            self.dismiss_schedule.cancel()
        MessagePopup.current = None
