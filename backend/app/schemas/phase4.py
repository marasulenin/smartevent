from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WishlistOut(BaseModel):
    id: int
    event_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventUpdateCreate(BaseModel):
    message: str = Field(min_length=3, max_length=2000)
    is_important: bool = False

class EventUpdateOut(BaseModel):
    id: int
    event_id: int
    author_id: int
    message: str
    is_important: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=50)
    email: str | None = Field(default=None, min_length=5, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
