from tinydb import TinyDB
import guest
from datetime import date

date = {"journey": "Kimberley Quest",
        "start": date.today().strftime("%d%m%y")}

data = '''Smith,Peter,1,43,M,Vegetarian food only,"13 Wallaby Way, Port Jackson. NSW."
Smith,Le-Anne,1,40,F,Vegetarian food only,"13 Wallaby Way, Port Jackson. NSW."
Bloggs,Jack,2,35,M,,"3 Roselea Drive, Roselea. VIC."
Bloggs,Jenny,2,37,F,,"3 Roselea Drive, Roselea. VIC."
Jones,Sarah,3,27,F,,"63 Smith Street, Brisbane, QLD"
Jackson,Roger,4,31,M,,"45 Pottsville Rd, Petersham. NSW"
Phillips,Jack,5,56,M,Difficulty walking long distances,"345 Redmire Street,Vancouver, BC. Canada"
Phillips,Kerry,5,50,F,,"345 Redmire Street,Vancouver, BC. Canada"
Ngoc van,Vo,6,67,M,Pacemaker – Heart Issues,"93 Nguyen Thai Hoc Street, Cau Ong Lanh Ward, Dist 1 "
Ngoc van,Yoon,6,64,F,Vegetarian food only,"93 Nguyen Thai Hoc Street, Cau Ong Lanh Ward, Dist 1"
Tanaka,Taro,7,56,M,Vegetarian food only,"5-2-1 Ginza, Chou-ku Tokyo 170-3293"
Tanaka,WanLee,7,54,M,Vegetarian food only,"5-2-1 Ginza, Chou-ku Tokyo 170-3293"'''

guests = []

for line in data.split('\n'):
    profile = line.split(',')
    last, first, cabin, age, gender, notes, *_ = profile
    address = ''.join(profile[6:]).replace('"', '')
    hashed = guest.hash_psw("123456")
    bookings = ["No Activity" for _ in range(14)]
    meals = ["Normal meal" for _ in range(14)]
    guests.append({"username": first[0] + last + str(cabin),
                   "hash": hashed,
                   "last": last,
                   "first": first,
                   "cabin": int(cabin),
                   "age": int(age),
                   "gender": gender,
                   "notes": notes,
                   "address": address,
                   "activities": bookings,
                   "meals": meals})

db = TinyDB("guest.json", indent=2)
db.purge_tables()
db.insert(date)
table_profile = db.table("profiles")
for guest in guests:
    table_profile.insert(guest)
