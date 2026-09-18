from fastapi import FastAPI, HTTPException, Depends
from datenbank.SQL_db import del_user, add_user, show_users, add_licence, show_licence, get_user_verifying, is_admin
from pydantic import BaseModel
from functions.password_hasher import hashing_password
from datetime import date, datetime
from functions.password_verifyer import verifying_pw
from functions.create_acces_token import create_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functions.token_verifyer import verify_token

security = HTTPBearer()
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

class LoginData(BaseModel):
    email: str
    password: str



def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    token_sub = verify_token(token)
    if isinstance(token_sub,int):
        if is_admin(token_sub):
            return True
        raise HTTPException(status_code=403,
                            detail="Not An Admin")
    match token_sub:
        case "Token abgelaufen":
            raise HTTPException(status_code=401,
                                detail="Token expired")
        case "Token ist invalide":
            raise HTTPException(status_code=401,
                                detail="Token Not Valid")
        case "Ein fehler ist aufgetreten, bei verify Token":
            raise HTTPException(status_code=500,
                                detail="Something Went Wrong Handling The Token")
        case "JWT_SECRET fehlt":
            raise HTTPException(status_code=500,
                                detail="JWT Secret Is Missing")
        case _: 
            raise HTTPException(status_code=500,
                                detail="Somethin Went Wrong Verifying your Token")

@app.get("/health/live")
def health_live():
    return True

@app.post("/user/add")
def adding_user(user: UserCreate,_: bool = Depends(verify_admin)):
    hashed_password = hashing_password(user.password)
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
def deleting_user(user_id: int,_: bool = Depends(verify_admin)):
    return del_user(user_id)



@app.get("/users/show", response_model=list[UserShowResponse])
def showing_users(_: bool = Depends(verify_admin)):
    users = show_users()
    return users

        

@app.post("/licence/add")
def adding_licence(licence: LicenceCreate, _: bool = Depends(verify_admin)):
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
def showing_licence(_: bool = Depends(verify_admin)):
    licences = show_licence()
    return licences


@app.post("/user/login")
def login(login_data: LoginData):
    code = verifying_pw(login_data.email, login_data.password)

    match code:
        case "User mit dieser email existiert nicht":
            raise HTTPException(status_code=401,
                            detail="Invalid email or password")
        
        case "User hat keine gültige Lizenz":
            raise HTTPException(status_code=403,
                detail="This Email does not have a valid license")

        case "Eingeloggt":
            user_data = get_user_verifying(login_data.email)
            if isinstance(user_data, str):
                    raise HTTPException(
                    status_code=500,
                    detail="Unexpected internal state"
                    )
            token = create_token(user_data[0]["id"])

            if token:
                return {"detail": "You are logged in!",
                        "access_token": token,
                        "token_type": "bearer"}
            else:
                raise HTTPException(
                        status_code=500,
                        detail="Unexpected internal state"
                        )

        case "Falsches Passwort":
            raise HTTPException(status_code=401,
                detail="Invalid email or password")

        case _:  
            raise HTTPException(status_code=500,
                                detail="Something happend that we didnt Expect")

