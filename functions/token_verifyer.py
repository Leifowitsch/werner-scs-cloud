import os
import jwt


def verify_token(token):
    try:
        secret = os.getenv("JWT_SECRET")
        if not secret:
            return "JWT_SECRET fehlt"

        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"]
        )
        user_id = int(payload["sub"])
        return user_id
    except jwt.ExpiredSignatureError:
        return "Token abgelaufen"
    except jwt.InvalidTokenError:
        return "Token ist invalide"
    except Exception:
        return "Ein fehler ist aufgetreten, bei verify Token"
