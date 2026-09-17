from fastapi import FastAPI, HTTPException
from datenbank.SQL_db import del_user, add_user, show_users, add_licence, show_licence
from pydantic import BaseModel
from pwdlib import PasswordHash
from datetime import date, datetime

password_hash = PasswordHash.recommended()
app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserShowResponse(BaseModel):
    id: int
    name: str
    email: str
    admin: bool

class LicenceCreate(BaseModel):
    user_id: int
    valid_from: date
    valid_until: date

class LicenceShowResponse(BaseModel):
    id: int
    user_id: int
    valid_from: date
    valid_until: date
    active: bool
    created_at: datetime



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


@app.get("/users/show", response_model=list[UserShowResponse])
def showing_users():
    users = show_users()
    return users

@app.post("/licence/add")
def adding_licence(licence: LicenceCreate):

    code = add_licence(licence.user_id, licence.valid_from, licence.valid_until)

    match code:
        case "Invalid date range":
            raise HTTPException(status_code=400,
                                detail="The range of Validation is not allowed")
        case "licence added":
            return {"detail": "Everything Worked Just Fine!"}
        case "licence not added":
            raise HTTPException(status_code=500,
                                detail="Licence could not be added")
        case _:  
            raise HTTPException(status_code=500,
                                detail="Something happend that we didnt Expect")

@app.get("/licence/show", response_model=list[LicenceShowResponse])
def showing_licence():
    licences = show_licence()
    return licences