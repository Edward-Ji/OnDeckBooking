from tinydb import TinyDB, Query
from random import choice
from datetime import date

activity_details = [{"name": "Glass bottom explorer",
                     "rating": "easy",
                     "desc": "Experience a day on the reef and a short walk on one of the many remote beaches. Our "
                             "glass bottom boat experience is second to none.",
                     "price": 120},
                    {"name": "Flying to fishing",
                     "rating": "moderate",
                     "desc": "Take our helicopter transfer and walk to a fishing spot where the fish are always biting."
                             " Lunch will be the fish caught and cooked on the spot.",
                     "price": 300},
                    {"name": "SCUBA adventure",
                     "rating": "challenging",
                     "desc": "Enjoy the whole day out in a SCUBA diving adventure. You will be transferred from the "
                             "Kimberley Quest to a purpose-built pontoon, where you will dive and lunch in style "
                             "(participants must be PADI certified for open water diving).",
                     "price": 160},
                    {"name": "Feeding crocodile",
                     "rating": "challenging",
                     "desc": "You will visit the native crocodiles on the Karona island that bites by a fast boat. "
                             "You may feed them with special equipments if you wish. ",
                     "price": 120},
                    {"name": "Individual fishing",
                     "rating": "moderate",
                     "desc": "You will ride a boat and go fishing on your own or you could go in small groups. "
                             "Out in the middle of the Mozo River, you will be fishing or your own. "
                             "According to local laws, you can keep the spoil. ",
                     "price": 246},
                    {"name": "Swim in Mozo",
                     "rating": "challenging",
                     "desc": "Enjoy a swim in the calm Mozo river. "
                             "A safeguard will follow you, but please still make sure you can swim on your own. ",
                     "price": 80},
                    {"name": "Visiting aircraft remains",
                     "rating": "easy",
                     "desc": "In this activity, you will visit the remains of a aircraft that went down in the 1980s. "
                             "Out on the island, you will have a wonderful view of local wild life. "
                             "We will also have a picnic on the island.",
                     "price": 135},
                    {"name": "Waterfall bath",
                     "rating": "moderate",
                     "desc": "You will mostly stay on the rocky embankment under a beautiful waterfall. "
                             "However, the water could potentially flush you down the stream, "
                             "so make sure you can swim with ease. We will also provide life buoy. ",
                     "price": 85}]

activity_calendar = []

for day in range(1, 15):
    if day <= 3:
        activity_calendar.append({"day": day,
                                  "easy": None,
                                  "moderate": None,
                                  "challenging": None})
    else:
        activity_calendar.append({"day": day,
                                  "easy": choice(["Glass bottom explorer", "Visiting aircraft remains"]),
                                  "moderate": choice(["Flying to fishing", "Individual fishing", "Waterfall bath"]),
                                  "challenging": choice(["SCUBA adventure", "Feeding crocodile", "Swim in Mozo"])})

db = TinyDB("activity.json", indent=2)
db.purge_tables()
db.insert({"start": date.today().strftime("%d%m%y")})
tb_detail = db.table("details")
for each in activity_details:
    tb_detail.insert(each)
tb_calendar = db.table("calendar")
for each in activity_calendar:
    tb_calendar.insert(each)
