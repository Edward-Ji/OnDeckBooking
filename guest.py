import binascii
from datetime import date, datetime
import hashlib
import os
from tinydb import TinyDB, Query

# constant variables
SALT = b"sr0te2eQ20Klubmyie"
ACTIVITY_IMG_DIR = "res/activity_img"
UNKNOWN_ACTIVITY_IMG = "activity_unknown.png"
MEAL_IMG_DIR = "res/meal_img"

NO_ACTIVITY = {"name": "No Activity",
               "rating": "easy",
               "desc": "Stay on the cruise and enjoy the wonderful seascape and facilities that we offer.",
               "price": 0}

# initiate tinydb objects and load files
db_guest = TinyDB("guest.json", indent=2)
tb_profiles = db_guest.table("profiles")
db_activity = TinyDB("activity.json", indent=2)
tb_details = db_activity.table("details")
tb_calendar = db_activity.table("calendar")
db_meal = TinyDB("meal.json", indent=2)
query = Query()


# return hash of given password
def hash_psw(psw):
    pwd_hash = hashlib.pbkdf2_hmac('sha512', psw.encode('utf-8'), SALT, 100000)
    pwd_hash = binascii.hexlify(pwd_hash)
    return pwd_hash.decode('ascii')


# verify password by comparing its hash to stored hash
def verify_psw(psw, stored_hash):
    return hash_psw(psw) == stored_hash


# find image of given name in given path
def find_img(name, path):
    img_name = name.lower().replace(' ', '_')
    for root, dirs, files in os.walk(path):
        for fname in files:
            if fname.startswith(img_name):  # ignore extension
                return os.path.join(root, fname)
    return os.path.join(path, UNKNOWN_ACTIVITY_IMG)


# get the number of days from start
def get_day():
    journey = db_guest.get(query.journey == "Kimberley Quest")
    start_date = datetime.strptime(journey["start"], "%d%m%y")
    return (datetime.today() - start_date).days + 1


class Activity:

    BOOK_AHEAD = 3

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.rating = kwargs.pop("rating")
        self.desc = kwargs.pop("desc")
        self.price = kwargs.pop("price")
        if "day" in kwargs:
            self.day = kwargs.pop("day")

    @property
    def img(self):
        return find_img(self.name, ACTIVITY_IMG_DIR)

    @classmethod
    def no_activity(cls):
        return cls(**NO_ACTIVITY)

    @classmethod
    def find(cls, name):
        details = tb_details.get(query.name == name)
        return cls(**details)

    @classmethod
    def on_day(cls, day):
        # return the activities available for given day
        data = tb_calendar.get(query.day == day)
        activities = {}
        for rating, name in data.items():
            if rating != "day":
                activities[rating] = cls.find(name)
        # always add no activity to the list
        activities["no activity"] = cls.no_activity()
        return activities


class Meal:

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.desc = kwargs.pop("desc")
        if "day" in kwargs:
            self.day = kwargs.pop("day")

    @property
    def img(self):
        return find_img(self.name, MEAL_IMG_DIR)

    @classmethod
    def load(cls):
        for info in db_meal.all():
            yield cls(**info)


class Guest:

    logged_in = ''

    @staticmethod
    def find(username):
        # return dictionary of user profiles that match the username
        return tb_profiles.search(query.username == username)

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
        if not verify_psw(ori_psw, ori_hash):
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
        # get given criteria from profile of logged-in user
        profile = tb_profiles.get(query.username == cls.logged_in)
        return profile[criteria]

    @classmethod
    def set_profile(cls, criteria, value):
        # update given criteria in profile of logged-in user
        tb_profiles.update({criteria: value}, query.username == cls.logged_in)
        if criteria == "username":
            cls.logged_in = value

    @classmethod
    def get_booked(cls, criteria, day):
        # get the name of booked activity on given day
        bookings = cls.get_profile(criteria)
        return bookings[day-1]

    @classmethod
    def book_activity(cls, criteria, day, item):
        # update activity booking
        if not cls.logged_in:
            return

        def update_booking(d, a):  # change given day of booking list criteria
            def transform(doc):
                doc[criteria][d-1] = a  # criteria could be activity or meal
            return transform

        tb_profiles.update(update_booking(day, item), query.username == cls.logged_in)

    @classmethod
    def costs(cls):
        # return sum of all activity costs
        if not cls.logged_in:
            return
        receipt = []
        total = 0
        bookings = tb_profiles.get(query.username == cls.logged_in)["activities"]
        day_count = 1
        for name in bookings:
            if name != Activity.no_activity().name:  # leave out no activity
                activity = Activity.find(name)
                activity.day = day_count
                receipt.append(activity)
                total += activity.price
            day_count += 1
        return receipt, total
