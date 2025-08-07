from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies.database import get_db
from ..controllers.promotions import (
    create_promotion, get_promotions, get_promotion, update_promotion,
    delete_promotion, apply_promotion, validate_promotion_code
)
from ..schemas.promotions import PromotionCreate, PromotionUpdate, PromotionOut, PromotionApply

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.post("/", response_model=PromotionOut)
def create_promotion_endpoint(promotion: PromotionCreate, db: Session = Depends(get_db)):
    """Create a new promotion code"""
    return create_promotion(db, promotion)


@router.get("/", response_model=List[PromotionOut])
def list_promotions(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = Query(True, description="Show only active promotions"),
    db: Session = Depends(get_db)
):
    """Get all promotions with optional filtering"""
    return get_promotions(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/{promotion_id}", response_model=PromotionOut)
def get_promotion_endpoint(promotion_id: int, db: Session = Depends(get_db)):
    """Get a specific promotion by ID"""
    return get_promotion(db, promotion_id)


@router.put("/{promotion_id}", response_model=PromotionOut)
def update_promotion_endpoint(promotion_id: int, promotion: PromotionUpdate, db: Session = Depends(get_db)):
    """Update a promotion"""
    return update_promotion(db, promotion_id, promotion)


@router.delete("/{promotion_id}")
def delete_promotion_endpoint(promotion_id: int, db: Session = Depends(get_db)):
    """Deactivate a promotion"""
    return delete_promotion(db, promotion_id)


@router.post("/apply")
def apply_promotion_endpoint(promo_apply: PromotionApply, db: Session = Depends(get_db)):
    """Apply a promotion code to calculate discount"""
    return apply_promotion(db, promo_apply)


@router.get("/validate/{code}")
def validate_promotion_code_endpoint(code: str, db: Session = Depends(get_db)):
    """Validate if a promotion code is valid"""
    is_valid = validate_promotion_code(db, code)
    return {"code": code, "is_valid": is_valid}
