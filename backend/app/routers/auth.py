
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserRegister, UserResponse
from app.utils.dependencies import get_current_user
from app.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new SmartEvent user.

    Allowed registration roles:
        USER
        ORGANIZER

    ADMIN accounts cannot be created through public registration.
    """

    # --------------------------------------------------------
    # Check duplicate username
    # --------------------------------------------------------

    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # --------------------------------------------------------
    # Validate role
    # --------------------------------------------------------

    requested_role = user_data.role.upper()

    if requested_role not in {"USER", "ORGANIZER"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Allowed roles are USER and ORGANIZER.",
        )

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    hashed_password = hash_password(
        user_data.password
    )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=requested_role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.

    OAuth2 uses:
        username = user's email
        password = user's password

    JWT contains:
        user ID
        user role
        expiration time
    """

    # --------------------------------------------------------
    # Find user by email
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Create JWT with user ID + role
    # --------------------------------------------------------

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# PROFILE
# ============================================================

@router.get(
    "/profile",
    response_model=UserResponse,
)
def profile(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user's profile.
    """

    return current_user
