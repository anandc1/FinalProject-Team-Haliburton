from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    order_number: str
    customer_name: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = None


class ReviewUpdate(BaseModel):
    is_approved: Optional[bool] = None


class ReviewOut(BaseModel):
    id: int
    order_number: str
    customer_name: str
    rating: int
    review_text: Optional[str] = None
    is_approved: bool
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, etc.}
