
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# USER REGISTER
# ============================================================

class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
    )

    role: str = Field(
        default="USER",
        pattern="^(USER|ORGANIZER)$",
    )


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# TOKEN
# ============================================================

class Token(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# TOKEN DATA
# ============================================================

class TokenData(BaseModel):
    user_id: int | None = None
    role: str | None = None
