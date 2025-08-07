from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies.database import get_db
from ..controllers.reviews import (
    create_review, get_reviews, get_review, update_review, 
    delete_review, get_review_statistics
)
from ..schemas.reviews import ReviewCreate, ReviewUpdate, ReviewOut, ReviewStats

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut)
def create_review_endpoint(review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new customer review"""
    return create_review(db, review)


@router.get("/", response_model=List[ReviewOut])
def list_reviews(
    skip: int = 0, 
    limit: int = 100, 
    approved_only: bool = Query(True, description="Show only approved reviews"),
    db: Session = Depends(get_db)
):
    """Get all reviews with optional filtering"""
    return get_reviews(db, skip=skip, limit=limit, approved_only=approved_only)


@router.get("/{review_id}", response_model=ReviewOut)
def get_review_endpoint(review_id: int, db: Session = Depends(get_db)):
    """Get a specific review by ID"""
    return get_review(db, review_id)


@router.put("/{review_id}", response_model=ReviewOut)
def update_review_endpoint(review_id: int, review: ReviewUpdate, db: Session = Depends(get_db)):
    """Update a review (admin only - for approval)"""
    return update_review(db, review_id, review)


@router.delete("/{review_id}")
def delete_review_endpoint(review_id: int, db: Session = Depends(get_db)):
    """Delete a review"""
    return delete_review(db, review_id)


@router.get("/stats/summary", response_model=ReviewStats)
def get_review_statistics_endpoint(db: Session = Depends(get_db)):
    """Get review statistics for analytics"""
    return get_review_statistics(db)
