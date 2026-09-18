import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

def create_token(user_id: int):
    secret = os.getenv("JWT_SECRET")
    zeit_bis_ablauf = int(os.getenv("ABLAUF_ZEIT_MIN", "45"))
    if secret:

        ablauf_zeit = datetime.now(timezone.utc) + timedelta(minutes=zeit_bis_ablauf)

        payload = {
            "sub": str(user_id),
            "exp": ablauf_zeit
        }

        token = jwt.encode(key=secret, payload=payload, algorithm="HS256")
        return token
    else:
        return None
