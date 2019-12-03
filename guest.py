import binascii
import hashlib
import os
from tinydb import TinyDB, Query

SALT = b"sr0te2eQ20Klubmyi"

db = TinyDB("profile.json")
query = Query()


def hash_psw(psw):
    pwd_hash = hashlib.pbkdf2_hmac('sha512', psw.encode('utf-8'), SALT, 100000)
    pwd_hash = binascii.hexlify(pwd_hash)
    return pwd_hash.decode('ascii')


def verify_psw(psw, stored_hash):
    pwd_hash = hashlib.pbkdf2_hmac('sha512', psw.encode('utf-8'), SALT, 100000)
    pwd_hash = binascii.hexlify(pwd_hash).decode('ascii')
    return pwd_hash == stored_hash


class Guest:
    logged_in = None

    @staticmethod
    def find(username):
        # return a dictionary of user profiles that match the username
        return db.search(query.username == username)

    @classmethod
    def login(cls, usr, psw):
        found = cls.find(usr)
        if not found:
            return "User not found!"
        else:
            p_hash = found[0]["hash"]
            if p_hash == hash_psw(psw):
                return None
            else:
                return "Incorrect password!"


print(Guest.find("Smith"))
