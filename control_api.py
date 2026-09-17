from fastapi import FastAPI, HTTPException
from datenbank.SQL_db import del_user, add_user
from pydantic import BaseModel
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()
app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

@app.get("/health/live")
def health_live():
    return True

@app.post("/user/add")
def adding_user(user: UserCreate):
    hashed_password = password_hash.hash(user.password)
    code = add_user(user.name, user.email, hashed_password)

    match code:
        case "email in use":
            raise HTTPException(status_code=409,
                              detail="Email already in use")
        case "user added":
            return {"detail": "Everything Worked Just Fine!"}
        case "user not added":
            raise HTTPException(status_code=500,
                              detail="User could not be added")
        case _:  
            raise HTTPException(status_code=500,
                              detail="Something happend that we didnt Expect")


@app.delete("/user/del/{user_id}")
def deleting_user(user_id: int):
    return del_user(user_id)
