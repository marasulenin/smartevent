from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token


# ============================================================
# OAUTH2 CONFIGURATION
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the currently authenticated user from the JWT token.
    """

    token_data = decode_access_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = token_data["user_id"]

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return user


# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

def require_roles(*allowed_roles: str):
    """
    Create a dependency that allows only specific user roles.

    Example:

        Depends(require_roles("ADMIN"))

    Or:

        Depends(require_roles("ADMIN", "ORGANIZER"))
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to access "
                    "this resource"
                ),
            )

        return current_user

    return role_checker


# ============================================================
# ROLE-SPECIFIC DEPENDENCIES
# ============================================================

def get_current_user_role(
    current_user: User = Depends(get_current_user),
) -> str:
    """
    Return the current user's role.
    """
    return current_user.role


def require_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow USER role only.
    """
    if current_user.role != "USER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="USER role required",
        )

    return current_user


def require_organizer(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow ORGANIZER role only.
    """
    if current_user.role != "ORGANIZER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ORGANIZER role required",
        )

    return current_user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow ADMIN role only.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ADMIN role required",
        )

    return current_user