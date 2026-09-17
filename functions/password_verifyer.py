from datenbank.SQL_db import get_user_verifying
from functions.password_hasher import password_hash
from datetime import date


def verifying_pw(email: str, password: str):
    pw_match = False
    licence_active=False
    user_data = get_user_verifying(email)
    if isinstance(user_data, str):
        return "User mit dieser email existiert nicht"
    if  password_hash.verify(password, user_data[0]["hashed_password"]):
            pw_match = True
    for licence in user_data[1]:
        if licence["valid_from"] <= date.today() <=licence["valid_until"] and licence["active"]:
            licence_active = True
            break

    if licence_active and pw_match:
         return "Eingeloggt"

    if not pw_match:
         return "Falsches Passwort"
    return "User hat keine gültige Lizenz"

