from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PromotionCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    description: Optional[str] = None
    discount_percent: int = Field(..., ge=1, le=100, description="Discount percentage")
    min_order_amount_cents: int = Field(0, ge=0, description="Minimum order amount for discount")
    max_discount_cents: Optional[int] = Field(None, ge=0, description="Maximum discount amount")
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1, description="Usage limit for promo code")


class PromotionUpdate(BaseModel):
    description: Optional[str] = None
    discount_percent: Optional[int] = Field(None, ge=1, le=100)
    min_order_amount_cents: Optional[int] = Field(None, ge=0)
    max_discount_cents: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)


class PromotionOut(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    discount_percent: int
    min_order_amount_cents: int
    max_discount_cents: Optional[int] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    usage_limit: Optional[int] = None
    times_used: int

    class ConfigDict:
        from_attributes = True


class PromotionApply(BaseModel):
    code: str
    order_total_cents: int
