from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
from ..models.reviews import Review
from ..models.orders import Order
from ..schemas.reviews import ReviewCreate, ReviewUpdate, ReviewOut, ReviewStats


def create_review(db: Session, review: ReviewCreate) -> ReviewOut:
    # Verify order exists
    order = db.query(Order).filter(Order.order_number == review.order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if review already exists for this order
    existing_review = db.query(Review).filter(Review.order_number == review.order_number).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Review already exists for this order")
    
    db_review = Review(
        order_number=review.order_number,
        customer_name=review.customer_name,
        rating=review.rating,
        review_text=review.review_text
    )
    
    try:
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return ReviewOut.from_orm(db_review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Review creation failed")


def get_reviews(db: Session, skip: int = 0, limit: int = 100, approved_only: bool = True):
    query = db.query(Review)
    if approved_only:
        query = query.filter(Review.is_approved == True)
    return query.offset(skip).limit(limit).all()


def get_review(db: Session, review_id: int) -> Review:
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


def update_review(db: Session, review_id: int, review: ReviewUpdate) -> ReviewOut:
    db_review = get_review(db, review_id)
    
    if review.is_approved is not None:
        db_review.is_approved = review.is_approved
    
    db.commit()
    db.refresh(db_review)
    return ReviewOut.from_orm(db_review)


def delete_review(db: Session, review_id: int):
    db_review = get_review(db, review_id)
    db.delete(db_review)
    db.commit()
    return {"message": "Review deleted"}


def get_review_statistics(db: Session) -> ReviewStats:
    """Get review statistics for analytics"""
    reviews = db.query(Review).filter(Review.is_approved == True).all()
    
    if not reviews:
        return ReviewStats(
            total_reviews=0,
            average_rating=0.0,
            rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        )
    
    total_reviews = len(reviews)
    total_rating = sum(review.rating for review in reviews)
    average_rating = round(total_rating / total_reviews, 2)
    
    # Calculate rating distribution
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1
    
    return ReviewStats(
        total_reviews=total_reviews,
        average_rating=average_rating,
        rating_distribution=rating_distribution
    )
