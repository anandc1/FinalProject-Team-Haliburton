from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .order_details import OrderDetail


class OrderItemCreate(BaseModel):
    dish_id: int
    qty: int


class GuestOrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None
    is_delivery: bool = False
    payment_method: Optional[str] = None  # cash, card, online
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str  # pending, confirmed, preparing, ready, out_for_delivery, delivered, cancelled


class PaymentUpdate(BaseModel):
    payment_status: str  # pending, paid, failed
    payment_method: Optional[str] = None


class OrderBase(BaseModel):
    customer_name: str
    description: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    description: Optional[str] = None


class OrderOut(BaseModel):
    order_number: str
    id: int
    status: str
    total_cents: int
    payment_method: Optional[str] = None
    payment_status: str
    items: List[OrderDetail]
    created_at: datetime
    is_delivery: bool

    class ConfigDict:
        from_attributes = True


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    order_details: list[OrderDetail] = None

    class ConfigDict:
        from_attributes = True
