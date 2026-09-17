from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

def hashing_password(password: str):
    hashed_password = password_hash.hash(password)
    return hashed_password
