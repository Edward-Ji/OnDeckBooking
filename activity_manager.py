from tinydb import TinyDB, Query

activity_details = [{"name": "Glass bottom explorer",
                     "desc": "Experience a day on the reef and a short walk on one of the many remote beaches. Our "
                             "glass bottom boat experience is second to none.",
                     "price": 120},
                    {"name": "Flying to fishing",
                     "desc": "Take our helicopter transfer and walk to a fishing spot where the fish are always biting."
                             " Lunch will be the fish caught and cooked on the spot.",
                     "price": 290},
                    {"name": "SCUBA adventure",
                     "desc": "Enjoy the whole day out in a SCUBA diving adventure. You will be transferred from the "
                             "Kimberley Quest to a purpose-built pontoon, where you will dive and lunch in style "
                             "(participants must be PADI certified for open water diving).",
                     "price": 160}]

activity_calendar = []

for day in range(1, 15):
    if day <= 3:
        activity_calendar.append({"day": day,
                                  "easy": None,
                                  "moderate": None,
                                  "challenging": None})
    else:
        activity_calendar.append({"day": day,
                                  "easy": "Glass bottom explorer",
                                  "moderate": "Flying to fishing",
                                  "challenging": "SCUBA adventure"})

db = TinyDB("activity.json", indent=2)
db.purge()
tb_detail = db.table("details")
for each in activity_details:
    tb_detail.insert(each)
tb_calendar = db.table("calendar")
for each in activity_calendar:
    tb_calendar.insert(each)
