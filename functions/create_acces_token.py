import os
import jwt
from datetime import datetime, timedelta, timezone


def create_token(user_id: int):
    secret = os.getenv("JWT_SECRET")
    if secret:

        ablauf_zeit = datetime.now(timezone.utc) + timedelta(minutes=45)

        payload = {
            "sub": str(user_id),
            "exp": ablauf_zeit
        }

        token = jwt.encode(key=secret, payload=payload, algorithm="HS256")
        return token
    else:
        return None
