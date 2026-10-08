from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password before storing it in the database.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Compare a plain-text password with its stored hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# JWT TOKEN
# ============================================================

def create_access_token(
    user_id: int,
    role: str,
) -> str:
    """
    Create a JWT access token containing:
        - user ID
        - user role
        - expiration time
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode and validate a JWT token.

    Returns:
        {
            "user_id": int,
            "role": str
        }

        or None if the token is invalid/expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")
        role = payload.get("role")

        if user_id is None:
            return None

        return {
            "user_id": int(user_id),
            "role": role,
        }

    except (JWTError, ValueError, TypeError):
        return None