import psycopg
import os
from datetime import date


def open_db_conn():
    return psycopg.connect(
            host="localhost",
            port=5432,
            dbname="SCS_KONVERTER",
            user="postgres",
            password=os.getenv("POSTGRES_PW")
        )

def add_user(name: str, email: str, hashed_password: str) -> str:
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s",
                        (email, ))
            email_exist = cur.fetchone()
            if email_exist:
                return "email in use"
            
            cur.execute("INSERT INTO users(name, email, hashed_password, admin) VALUES (%s,%s,%s,%s) RETURNING id",
                        (name,email,hashed_password,False))
            id_new = cur.fetchone()
            if id_new is not None:
                return "user added"
            return "user not added"

def del_user(user_id: int) -> bool:
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM lizenzen WHERE user_id = %s",
                        (user_id, ))
            cur.execute("DELETE FROM users WHERE id = %s RETURNING id",
                        (user_id, ))
            del_id = cur.fetchone()
            if del_id is None:
                return False
            return True

def show_users():
    list_users = []
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,name,email,admin FROM users")
            users = cur.fetchall()
            for user in users:
                list_users.append(
                    {"id": user[0],
                     "name": user[1],
                     "email": user[2],
                     "admin": user[3]}
                )

            return list_users


def add_licence(user_id: int, valid_from: date, valid_until: date):
    if valid_from > valid_until:
        return "Invalid date range"
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO lizenzen(user_id,valid_from,valid_until) VALUES(%s,%s,%s) RETURNING id",
                        (user_id,valid_from,valid_until))
            id_new = cur.fetchone()
            if id_new is not None:
                return "licence added"
            return "licence not added"

def show_licence():
    list_licence = []
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,user_id,valid_from,valid_until,active,created_at FROM lizenzen")
            licences = cur.fetchall()
            for licence in licences:
                list_licence.append(
                    {"id": licence[0],
                     "user_id": licence[1],
                     "valid_from": licence[2],
                     "valid_until": licence[3],
                     "active": licence[4],
                     "created_at": licence[5]
                     }
                )

            return list_licence

def get_user_verifying(email: str):
        list_licenses = []
        with open_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id,email,hashed_password FROM users WHERE email = %s",
                            (email, ))
                user = cur.fetchone()
                if user is not None:
                    user_dict = {
                    "id": user[0],
                    "email": user[1],
                    "hashed_password": user[2]
                             }
                    cur.execute("SELECT valid_from,valid_until,active FROM lizenzen WHERE user_id = %s",
                                (user[0], ))
                    licences = cur.fetchall()
                    for licence in licences:
                        list_licenses.append(
                        {"valid_from": licence[0],
                        "valid_until": licence[1],
                        "active": licence[2]}
                    )
                    return (user_dict, list_licenses)
                return "No user with this email"


def is_admin(user_id: int):
    with open_db_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT admin FROM users WHERE id = %s",
                                (user_id, ))
                    admin_tup = cur.fetchone()
                    if admin_tup is None:
                        return False
                    if admin_tup[0]:
                        return True
                    return False