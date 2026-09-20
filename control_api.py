from fastapi import FastAPI, HTTPException, Depends
from datenbank.SQL_db import del_user, add_user, show_users, add_licence, show_licence, get_user_verifying, is_admin
from pydantic import BaseModel
from functions.password_hasher import hashing_password
from datetime import date, datetime
from functions.password_verifyer import verifying_pw
from functions.create_acces_token import create_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functions.token_verifyer import verify_token
from datenbank.SQL_db_update_exe import get_active_release, add_release, activate_version,show_versions ,ReleaseAlreadyExistsError, ReleaseNotActiveError, ReleaseNotAddedError, ReleaseNotFoundError, NoActiveVersionError, MultActiveVersionError

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

class ReleaseShowResponse(BaseModel):
        version: str
        release_date: datetime
        size: int
        location: str
        checksum: str
        active: bool

class LoginData(BaseModel):
    email: str
    password: str

class AddRelease(BaseModel):
    version: str
    location: str

def token_handler(token_sub):
    if isinstance(token_sub,int):
        return token_sub
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


def verify_login(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = token_handler(verify_token(credentials.credentials))
    return user_id


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = verify_login(credentials)
    if is_admin(user_id):
        return True
    raise HTTPException(status_code=403,
                        detail="Not an Admin")

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


@app.get("/exe/version")
def get_exe_data():
    try:
        return get_active_release()
    except NoActiveVersionError:
        raise HTTPException(status_code=404,
                                detail="There Is No Active Version")

    except MultActiveVersionError:
        raise HTTPException(status_code=500,
                                detail="Multiple Versions Are Acitve")


@app.post("/exe/add")
def adding_release(data: AddRelease, _: bool = Depends(verify_admin)):
    try:


        add_release(data.version, data.location)
        return {"detail": "Everything Worked Just Fine!"}

    
    except ReleaseAlreadyExistsError:
        raise HTTPException(status_code=409,
                                detail="This version already exists")

    except ReleaseNotAddedError:
        raise HTTPException(status_code=500,
                                detail="This Version could not be released")


@app.put("/exe/{version_id}/activate")
def activate_exe(version_id: str,  _: bool = Depends(verify_admin)):
    try:

        activate_version(version_id)
        return {"detail": "Everything Worked Just Fine!"}

    except ReleaseNotFoundError:
        raise HTTPException(status_code=404,
                                detail="This version does not exist")

    except ReleaseNotActiveError:
        raise HTTPException(status_code=500,
                                detail="This Version could not be activated")

@app.get("/exe/show/versions", response_model=list[ReleaseShowResponse])
def show_exes(_: bool = Depends(verify_admin)):
    return show_versions()





