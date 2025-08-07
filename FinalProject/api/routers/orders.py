from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from typing import Optional
from ..controllers import orders as controller
from ..schemas import orders as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Orders'],
    prefix="/orders"
)


@router.post("/", response_model=schema.Order)
def create(request: schema.OrderCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Order])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Order)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Order)
def update(item_id: int, request: schema.OrderUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)


@router.post("/guest", response_model=schema.OrderOut)
def create_guest_order(request: schema.GuestOrderCreate, db: Session = Depends(get_db)):
    return controller.create_guest_order(db=db, payload=request)


@router.get("/{order_number}", response_model=schema.OrderOut)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    return controller.get_order_by_number(db=db, order_number=order_number)


@router.patch("/{order_number}/status")
def update_order_status(order_number: str, status_update: schema.OrderStatusUpdate, db: Session = Depends(get_db)):
    return controller.update_order_status(db=db, order_number=order_number, status_update=status_update)


@router.patch("/{order_number}/payment")
def update_payment_status(order_number: str, payment_update: schema.PaymentUpdate, db: Session = Depends(get_db)):
    return controller.update_payment_status(db=db, order_number=order_number, payment_update=payment_update)


@router.get("/", response_model=list[schema.OrderOut])
def get_orders_by_status(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return controller.get_orders_by_status(db=db, status=status, skip=skip, limit=limit)
