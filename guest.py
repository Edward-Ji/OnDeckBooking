import binascii
import hashlib
from kivy.properties import StringProperty
import os
from tinydb import TinyDB, Query

SALT = b"sr0te2eQ20Klubmyie"
ACTIVITY_IMG_DIR = "res/activity_img"

db_guest = TinyDB("guest.json", indent=2)
db_activity = TinyDB("activity.json", indent=2)
tb_details = db_activity.table("details")
tb_calendar = db_activity.table("calendar")
query = Query()


def hash_psw(psw):
    pwd_hash = hashlib.pbkdf2_hmac('sha512', psw.encode('utf-8'), SALT, 100000)
    pwd_hash = binascii.hexlify(pwd_hash)
    return pwd_hash.decode('ascii')


def verify_psw(psw, stored_hash):
    return hash_psw(psw) == stored_hash


def find_img(name):
    img_name = name.lower().replace(' ', '_')
    for root, dirs, files in os.walk(ACTIVITY_IMG_DIR):
        for fname in files:
            if img_name in fname:
                return os.path.join(root, fname)
    return os.path.join(ACTIVITY_IMG_DIR, "activity_unknown.png")


class Activity:

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.rating = kwargs.pop("rating")
        self.desc = kwargs.pop("desc")
        self.price = kwargs.pop("price")
        if "day" in kwargs:
            self.day = kwargs.pop("day")

    @property
    def img(self):
        return find_img(self.name)

    @classmethod
    def no_activity(cls):
        return cls(name="No Activity",
                   rating='easy',
                   desc="Stay on the cruise and enjoy the wonderful seascape and facilities that we offer.",
                   price=0)

    @classmethod
    def find(cls, name):
        details = tb_details.search(query.name == name)[0]
        return cls(**details)

    @classmethod
    def on_day(cls, day):
        data = tb_calendar.search(query.day == day)[0]
        activities = {}
        for rating, name in data.items():
            if rating != "day" and name:
                activities[rating] = cls.find(name)
        activities["no activity"] = cls.no_activity()
        return activities


class Guest:

    logged_in = ''

    @staticmethod
    def find(username):
        # return a dictionary of user profiles that match the username
        return db_guest.search(query.username == username)

    @classmethod
    def login(cls, usr, psw):
        found = cls.find(usr)
        if not found:
            return "User not found!"
        else:
            p_hash = found[0]["hash"]
            if p_hash == hash_psw(psw):
                cls.logged_in = usr
                return
            else:
                return "Incorrect password!"

    @classmethod
    def change_psw(cls, ori_psw, new_psw):
        ori_hash = cls.get_profile("hash")
        if verify_psw(ori_psw, ori_hash):
            return "Incorrect original password!"
        elif ori_psw == new_psw:
            return "Your new password is the same as the original one!"
        elif len(new_psw) < 6:
            return "You new password is too short!"
        else:
            cls.set_profile("hash", hash_psw(new_psw))


    @classmethod
    def logout(cls):
        cls.logged_in = None

    @classmethod
    def get_profile(cls, criteria):
        profile = db_guest.search(query.username == cls.logged_in)[0]
        return profile[criteria]

    @classmethod
    def set_profile(cls, criteria, value):
        db_guest.update({criteria: value}, query.username == cls.logged_in)
        if criteria == "username":
            cls.logged_in = value

    @classmethod
    def get_booked(cls, day):
        bookings = cls.get_profile("bookings")
        return bookings[day-1]

    @classmethod
    def book_activity(cls, day, activity):
        if not cls.logged_in:
            return

        def update_booking(d, a):
            def transform(doc):
                doc["bookings"][d-1] = a
            return transform

        db_guest.update(update_booking(day, activity), query.username == cls.logged_in)

    @classmethod
    def costs(cls):
        if not cls.logged_in:
            return
        receipt = []
        total = 0
        bookings = db_guest.search(query.username == cls.logged_in)[0]["bookings"]
        day_count = 1
        for name in bookings:
            if name != Activity.no_activity().name:
                activity = Activity.find(name)
                activity.day = day_count
                receipt.append(activity)
                total += activity.price
            day_count += 1
        return receipt, total
