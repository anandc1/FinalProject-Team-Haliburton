from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OrderDetailBase(BaseModel):
    qty: int
    unit_price_cents: int
    line_total_cents: int


class OrderDetailCreate(OrderDetailBase):
    order_id: int
    dish_id: int


class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    dish_id: Optional[int] = None
    qty: Optional[int] = None
    unit_price_cents: Optional[int] = None
    line_total_cents: Optional[int] = None


class OrderDetail(OrderDetailBase):
    id: int
    order_id: int
    dish_id: int

    class ConfigDict:
        from_attributes = True