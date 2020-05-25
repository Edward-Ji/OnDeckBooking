from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, StringProperty

import re
from tinydb import TinyDB, Query

db_help = TinyDB("help.json", indent=2)
query = Query()

RAPID_CLICK_INTERVAL = .35
PASSWORD_TIMEOUT = 3


class Cursor:
    _default = "arrow"
    trigger = None
    
    @classmethod
    def change(cls, widget, name):
        Window.set_system_cursor(name)
        cls.trigger = widget
    
    @classmethod
    def restore(cls, widget):
        if cls.trigger is widget:
            Window.set_system_cursor(cls._default)


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
            self.reset = Clock.schedule_once(lambda _: setattr(self, "press_count", 0), RAPID_CLICK_INTERVAL)
            if 5 <= self.press_count <= 9:
                MessagePopup(message="Tap {} more time(s) to enter debug mode!".format(10 - self.press_count)).open()
            elif self.press_count == 10:
                MessagePopup(message="You are now in debug mode!").open()
                App.get_running_app().root.current = "debug"


# provoke event upon the start and end of mouse hovering
class HoverWidget(Widget):
    hovered_ins = None
    hovered = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        self.register_event_type('on_hover_enter')
        self.register_event_type('on_hover_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverWidget, self).__init__(**kwargs)
    
    @property
    def in_view(self):
        root_widgets = App.get_running_app().root_window.children
        if not isinstance(root_widgets[0], MessagePopup):
            foremost = root_widgets[0]
        else:
            foremost = root_widgets[1]
        parent = self.parent
        while parent:
            temp = parent.parent
            if temp is foremost:
                return True
            if parent is temp:
                return False
            parent = temp
    
    def on_mouse_pos(self, *args):
        if not self.in_view:
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
    
    def on_touch_up(self, touch):
        self.on_hover_leave()
        self.hovered = False
        return super(HoverWidget, self).on_touch_up(touch)


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
class MainButton(HoverWidget, Button):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mask = None
    
    def on_hover_enter(self):
        # lighten the button upon mouse hover event
        with self.canvas:
            Color(rgba=(1, 1, 1, .08))
            self.mask = Rectangle(size=self.size,
                                  pos=self.pos)
        # set cursor icon to hand
        Cursor.change(self, "hand")
    
    def on_hover_leave(self):
        # restore button when mouse hover event ends
        if self.mask:
            self.canvas.remove(self.mask)
            self.mask = None
        # restore cursor icon back to arrow
        Cursor.restore(self)


# button displayed in the top bar
class HeadingButton(RoundedBehavior, HoverWidget, Button):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hint = None
    
    def on_hover_enter(self):
        # show function of button when mouse hovers
        self.hint = Label(text=self.name.title(),
                          center=(self.center_x, self.y - 6))
        self.add_widget(self.hint)
        # set cursor icon to hand
        Cursor.change(self, "hand")
    
    def on_hover_leave(self):
        # restore button when mouse leaves
        if self.hint:
            self.remove_widget(self.hint)
            self.hint = None
        # restore cursor icon back to arrow
        Cursor.restore(self)


class HelpButton(HeadingButton):
    screen = StringProperty()
    
    @property
    def content(self):
        content = db_help.get(query.screen == self.screen)["content"]
        return ''.join(content)
    
    def on_release(self):
        super(HelpButton, self).on_release()
        help_popup = MainPopup(title="Help")
        help_view = MainScrollView()
        help_label = MainLabel(text=self.content, color=(1, 1, 1, 1))
        help_view.add_widget(help_label)
        help_popup.content.add_widget(help_view)
        help_popup.open()
        help_label.text_size = help_popup.width - 18, None


class MainInput(TextInput, HoverWidget):
    
    def insert_text(self, substring, from_undo=False):
        # restrict input length to allowed length
        if len(self.text) + len(substring) > self.allowed_len:
            substring = substring[:self.allowed_len - len(self.text)]
        # restrict input to allowed pattern
        if not re.match(self.allowed_pat, substring):
            substring = ''
        return super().insert_text(substring, from_undo=from_undo)
    
    def on_hover_enter(self):
        if not self.disabled:
            Cursor.change(self, "ibeam")
        else:
            Cursor.change(self, "no")
    
    def on_hover_leave(self):
        Cursor.restore(self)
        
    def on_password(self, instance, value):
        # todo: temporary solution for cursor offset
        self.text += ' '
        self.text = self.text[:-1]


# toggle show and hide password in input box
class PasswordEye(HoverWidget, ToggleButton):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule_hide = None
        self.hint = None
        
    @property
    def hint_text(self):
        return "show" if self.state == "normal" else "hide"

    def on_hover_enter(self):
        # show function of button when mouse hovers
        self.hint = Label(text=self.hint_text,
                          color=(.3, .3, .3, 1),
                          center=(self.center_x, self.y - 6))
        self.add_widget(self.hint)
        # change cursor
        Cursor.change(self, "hand")

    def on_hover_leave(self):
        # restore button when mouse leaves
        if self.hint:
            self.remove_widget(self.hint)
            self.hint = None
        # restore cursor
        Cursor.restore(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # prevent de-focus on text inputs
            FocusBehavior.ignored_touch.append(touch)
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        return ToggleButton.on_touch_up(self, touch)

    def on_state(self, instance, value):
        if self.hint:
            self.hint.text = self.hint_text
        
        # change target input password state
        self.target.password = value == "normal"
        self.target.focus = True
        
        # automatically hide password two seconds after showing password
        if value == "down":
            if instance.schedule_hide:
                self.schedule_hide.cancel()
            self.schedule_hide = Clock.schedule_once(lambda _: setattr(self, "state", "normal"),
                                                     PASSWORD_TIMEOUT)
            

# close button on top right of popup
class PopupCloseButton(RoundedBehavior, HoverWidget, Button):
    
    def on_hover_enter(self):
        # set cursor icon to hand
        Cursor.change(self, "hand")
    
    def on_hover_leave(self):
        # restore cursor icon back to arrow
        Cursor.restore(self)


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


class MainScrollView(ScrollView):
    pass


Factory.register("RoundedWidget", RoundedBehavior)
Factory.register("HoverBehavior", HoverWidget)
