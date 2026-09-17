from datenbank.SQL_db import show_users
from control_api import password_hash


def verifying_pw(email: str, pw: str, hashed_pw: str):
    pw_match = False
    users = show_users()
    for user in users:
        if user.email and password_hash.hash(user.password)