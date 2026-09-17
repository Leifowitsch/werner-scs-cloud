import psycopg
import os

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
            
            cur.execute("INSERT INTO users(name, email, password, admin) VALUES (%s,%s,%s,%s) RETURNING id",
                        (name,email,hashed_password,False))
            id_new = cur.fetchone()
            if id_new is not None:
                return "user added"
            return "user not added"

def del_user(user_id: int) -> bool:
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s RETURNING id",
                        (user_id, ))
            del_id = cur.fetchone()
            if del_id is None:
                return False
            return True
