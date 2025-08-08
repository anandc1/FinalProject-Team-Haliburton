from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
from ..models.promotions import Promotion
from ..schemas.promotions import PromotionCreate, PromotionUpdate, PromotionOut, PromotionApply


def create_promotion(db: Session, promotion: PromotionCreate) -> PromotionOut:
    db_promotion = Promotion(
        code=promotion.code.upper(),
        description=promotion.description,
        discount_percent=promotion.discount_percent,
        min_order_amount_cents=promotion.min_order_amount_cents,
        max_discount_cents=promotion.max_discount_cents,
        expires_at=promotion.expires_at,
        usage_limit=promotion.usage_limit
    )
    
    try:
        db.add(db_promotion)
        db.commit()
        db.refresh(db_promotion)
        return PromotionOut.model_validate(db_promotion.__dict__)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Promotion code already exists")


def get_promotions(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    query = db.query(Promotion)
    if active_only:
        query = query.filter(Promotion.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_promotion(db: Session, promotion_id: int) -> Promotion:
    promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion


def update_promotion(db: Session, promotion_id: int, promotion: PromotionUpdate) -> PromotionOut:
    db_promotion = get_promotion(db, promotion_id)
    
    if promotion.description is not None:
        db_promotion.description = promotion.description
    if promotion.discount_percent is not None:
        db_promotion.discount_percent = promotion.discount_percent
    if promotion.min_order_amount_cents is not None:
        db_promotion.min_order_amount_cents = promotion.min_order_amount_cents
    if promotion.max_discount_cents is not None:
        db_promotion.max_discount_cents = promotion.max_discount_cents
    if promotion.is_active is not None:
        db_promotion.is_active = promotion.is_active
    if promotion.expires_at is not None:
        db_promotion.expires_at = promotion.expires_at
    if promotion.usage_limit is not None:
        db_promotion.usage_limit = promotion.usage_limit
    
    db.commit()
    db.refresh(db_promotion)
    return PromotionOut.model_validate(db_promotion.__dict__)


def delete_promotion(db: Session, promotion_id: int):
    db_promotion = get_promotion(db, promotion_id)
    db_promotion.is_active = False
    db.commit()
    return {"message": "Promotion deactivated"}


def apply_promotion(db: Session, promo_apply: PromotionApply) -> dict:
    """Apply promotion code to order and calculate discount"""
    promotion = db.query(Promotion).filter(
        Promotion.code == promo_apply.code.upper(),
        Promotion.is_active == True
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion code not found")
    
    # Check if promotion is expired
    if promotion.expires_at and promotion.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Promotion code has expired")
    
    # Check usage limit
    if promotion.usage_limit and promotion.times_used >= promotion.usage_limit:
        raise HTTPException(status_code=400, detail="Promotion code usage limit reached")
    
    # Check minimum order amount
    if promo_apply.order_total_cents < promotion.min_order_amount_cents:
        raise HTTPException(
            status_code=400, 
            detail=f"Minimum order amount not met. Required: ${promotion.min_order_amount_cents/100:.2f}"
        )
    
    # Calculate discount
    discount_amount = (promo_apply.order_total_cents * promotion.discount_percent) // 100
    
    # Apply maximum discount limit if set
    if promotion.max_discount_cents:
        discount_amount = min(discount_amount, promotion.max_discount_cents)
    
    final_total = promo_apply.order_total_cents - discount_amount
    
    return {
        "promotion_code": promotion.code,
        "discount_percent": promotion.discount_percent,
        "discount_amount_cents": discount_amount,
        "original_total_cents": promo_apply.order_total_cents,
        "final_total_cents": final_total,
        "savings_cents": discount_amount
    }


def validate_promotion_code(db: Session, code: str) -> bool:
    """Validate if promotion code is valid and can be used"""
    promotion = db.query(Promotion).filter(
        Promotion.code == code.upper(),
        Promotion.is_active == True
    ).first()
    
    if not promotion:
        return False
    
    # Check if expired
    if promotion.expires_at and promotion.expires_at < datetime.now():
        return False
    
    # Check usage limit
    if promotion.usage_limit and promotion.times_used >= promotion.usage_limit:
        return False
    
    return True
