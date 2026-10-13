from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ReviewCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(..., min_length=2, max_length=2000)

class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    review_text: str | None = Field(default=None, min_length=2, max_length=2000)

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    rating: int
    review_text: str
    created_at: datetime
    username: str | None = None
    model_config = ConfigDict(from_attributes=True)

class ReviewListResponse(BaseModel):
    average_rating: float
    review_count: int
    reviews: list[ReviewResponse]
