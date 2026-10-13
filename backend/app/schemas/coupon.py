from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.coupon import DiscountType


class CouponCreate(BaseModel):
    coupon_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )
    discount_type: DiscountType
    discount_value: float = Field(
        ...,
        gt=0,
    )
    minimum_booking_amount: float = Field(
        default=0,
        ge=0,
    )
    expiry_date: datetime
    usage_limit: int = Field(
        default=1,
        gt=0,
    )
    is_active: bool = True


class CouponValidateRequest(BaseModel):
    coupon_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )
    booking_amount: float = Field(
        ...,
        ge=0,
    )


class CouponResponse(BaseModel):
    id: int
    coupon_code: str
    discount_type: DiscountType
    discount_value: float
    minimum_booking_amount: float
    expiry_date: datetime
    usage_limit: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class CouponValidationResponse(BaseModel):
    valid: bool
    coupon_id: int | None = None
    coupon_code: str | None = None
    discount_amount: float = 0
    final_amount: float
    message: str