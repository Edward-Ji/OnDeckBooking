from tinydb import TinyDB

meal_options = [{"name": "Normal meal",
                 "desc": "Fresh and delicately cooked chicken, pork or beef, "
                         "combined with carefully assorted vegetables."},
                {"name": "Seafood meal",
                 "desc": "Delicious fish, prawn and crab we just caught from the sea."},
                {"name": "Vegetarian meal",
                 "desc": "Fresh and delicately assorted vegetables, "
                         "with delicious sauce."},
                {"name": "No food",
                 "desc": "Book only when you want no food on this day!"}]

db = TinyDB("meal.json", indent=2)
db.purge()
for option in meal_options:
    db.insert(option)
