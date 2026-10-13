from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking
from app.models.coupon import Coupon, DiscountType
from app.models.user import User
from app.schemas.coupon import (
    CouponCreate,
    CouponResponse,
    CouponValidateRequest,
    CouponValidationResponse,
)
from app.utils.dependencies import get_current_user, require_admin


router = APIRouter(
    prefix="/api/v1/coupons",
    tags=["Coupons"],
)


def validate_coupon(
    db: Session,
    code: str,
    booking_amount: float,
    user_id: int | None = None,
):
    coupon = (
        db.query(Coupon)
        .filter(Coupon.coupon_code == code.strip().upper())
        .first()
    )

    if not coupon or not coupon.is_active:
        raise HTTPException(
            status_code=400,
            detail="Invalid or inactive coupon",
        )

    if datetime.utcnow() > coupon.expiry_date:
        raise HTTPException(
            status_code=400,
            detail="Coupon has expired",
        )

    if booking_amount < coupon.minimum_booking_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum booking amount is ₹{coupon.minimum_booking_amount:.2f}",
        )

    used = (
        db.query(Booking)
        .filter(
            Booking.coupon_id == coupon.id,
            Booking.booking_status != "CANCELLED",
        )
        .count()
    )

    if used >= coupon.usage_limit:
        raise HTTPException(
            status_code=400,
            detail="Coupon usage limit reached",
        )

    if coupon.discount_type == DiscountType.PERCENTAGE:
        if coupon.discount_value > 100:
            raise HTTPException(
                status_code=400,
                detail="Invalid coupon percentage",
            )

        discount = booking_amount * coupon.discount_value / 100

    else:
        discount = min(
            coupon.discount_value,
            booking_amount,
        )

    return coupon, round(discount, 2)


@router.post(
    "",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_coupon(
    data: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    coupon_code = data.coupon_code.strip().upper()

    existing_coupon = (
        db.query(Coupon)
        .filter(Coupon.coupon_code == coupon_code)
        .first()
    )

    if existing_coupon:
        raise HTTPException(
            status_code=409,
            detail="Coupon code already exists",
        )

    if data.expiry_date <= datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Expiry date must be in the future",
        )

    if (
        data.discount_type == DiscountType.PERCENTAGE
        and data.discount_value > 100
    ):
        raise HTTPException(
            status_code=400,
            detail="Percentage discount cannot exceed 100",
        )

    coupon = Coupon(
        coupon_code=coupon_code,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        minimum_booking_amount=data.minimum_booking_amount,
        expiry_date=data.expiry_date,
        usage_limit=data.usage_limit,
        is_active=data.is_active,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    return coupon


@router.post(
    "/validate",
    response_model=CouponValidationResponse,
)
def validate(
    data: CouponValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        coupon, discount = validate_coupon(
            db,
            data.coupon_code,
            data.booking_amount,
            current_user.id,
        )

        return CouponValidationResponse(
            valid=True,
            coupon_id=coupon.id,
            coupon_code=coupon.coupon_code,
            discount_amount=discount,
            final_amount=round(
                data.booking_amount - discount,
                2,
            ),
            message="Coupon applied successfully",
        )

    except HTTPException as exc:
        return CouponValidationResponse(
            valid=False,
            discount_amount=0,
            final_amount=data.booking_amount,
            message=str(exc.detail),
        )