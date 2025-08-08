from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import orders as model
from ..models.dishes import Dish
from ..schemas.orders import GuestOrderCreate, OrderOut, OrderStatusUpdate, PaymentUpdate
from ..schemas.order_details import OrderDetail
from sqlalchemy.exc import SQLAlchemyError
import uuid


def create(db: Session, request):
    # Generate unique order number
    order_number = uuid.uuid4().hex[:12]
    
    new_item = model.Order(
        order_number=order_number,
        customer_name=request.customer_name,
        customer_phone="000-000-0000",  # Default phone for simple orders
        description=request.description,
        total_cents=0,  # Default total for simple orders
        is_delivery=False,  # Default to pickup
        payment_status="pending"  # Default payment status
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.Order).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def create_guest_order(db: Session, payload: GuestOrderCreate) -> OrderOut:
    # Validate each dish exists and qty >= 1
    dishes = {}
    total_cents = 0
    
    for item in payload.items:
        if item.qty < 1:
            raise HTTPException(status_code=422, detail=f"Quantity must be at least 1 for dish {item.dish_id}")
        
        dish = db.query(Dish).filter(Dish.id == item.dish_id, Dish.is_active == True).first()
        if not dish:
            raise HTTPException(status_code=404, detail=f"Dish {item.dish_id} not found")
        
        dishes[item.dish_id] = dish
        total_cents += dish.price_cents * item.qty
    
    # Generate unique order number
    order_number = uuid.uuid4().hex[:12]
    
    # Create order
    new_order = model.Order(
        order_number=order_number,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        customer_address=payload.customer_address,
        is_delivery=payload.is_delivery,
        payment_method=payload.payment_method,
        total_cents=total_cents
    )
    
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # Create order details
        from ..models.order_details import OrderDetail
        order_details = []
        
        for item in payload.items:
            dish = dishes[item.dish_id]
            line_total_cents = dish.price_cents * item.qty
            
            order_detail = OrderDetail(
                order_id=new_order.id,
                dish_id=item.dish_id,
                qty=item.qty,
                unit_price_cents=dish.price_cents,
                line_total_cents=line_total_cents
            )
            db.add(order_detail)
            order_details.append(order_detail)
        
        db.commit()
        
        # Return order with details
        from ..schemas.order_details import OrderDetail as OrderDetailSchema
        
        order_data = {
                "order_number": new_order.order_number,
                "id": new_order.id,
                "status": new_order.status.value,
                "total_cents": total_cents,
                "payment_method": new_order.payment_method,
                "payment_status": new_order.payment_status,
                "items": [OrderDetailSchema(
                    id=detail.id,
                    order_id=detail.order_id,
                    dish_id=detail.dish_id,
                    qty=detail.qty,
                    unit_price_cents=detail.unit_price_cents,
                    line_total_cents=detail.line_total_cents
                ) for detail in order_details],
                "created_at": new_order.order_date,
                "is_delivery": new_order.is_delivery
            }
        return OrderOut.model_validate(order_data)
        
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=400, detail=error)


def get_order_by_number(db: Session, order_number: str):
    order = db.query(model.Order).filter(model.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order details
    from ..models.order_details import OrderDetail
    order_details = db.query(OrderDetail).filter(OrderDetail.order_id == order.id).all()
    
    from ..schemas.order_details import OrderDetail as OrderDetailSchema
    
    return OrderOut(
        order_number=order.order_number,
        id=order.id,
        status=order.status.value,
        total_cents=order.total_cents,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        items=[OrderDetailSchema(
            id=detail.id,
            order_id=detail.order_id,
            dish_id=detail.dish_id,
            qty=detail.qty,
            unit_price_cents=detail.unit_price_cents,
            line_total_cents=detail.line_total_cents
        ) for detail in order_details],
        created_at=order.order_date,
        is_delivery=order.is_delivery
    )


def update_order_status(db: Session, order_number: str, status_update: OrderStatusUpdate):
    """Update order status for real-time tracking"""
    order = db.query(model.Order).filter(model.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status
    valid_statuses = ["pending", "confirmed", "preparing", "ready", "out_for_delivery", "delivered", "cancelled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order.status = model.OrderStatus(status_update.status)
    db.commit()
    db.refresh(order)
    
    return {"message": f"Order status updated to {status_update.status}", "order_number": order_number}


def update_payment_status(db: Session, order_number: str, payment_update: PaymentUpdate):
    """Update payment status and method"""
    order = db.query(model.Order).filter(model.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate payment status
    valid_payment_statuses = ["pending", "paid", "failed"]
    if payment_update.payment_status not in valid_payment_statuses:
        raise HTTPException(status_code=400, detail="Invalid payment status")
    
    order.payment_status = payment_update.payment_status
    if payment_update.payment_method:
        order.payment_method = payment_update.payment_method
    
    db.commit()
    db.refresh(order)
    
    return {"message": f"Payment status updated to {payment_update.payment_status}", "order_number": order_number}


def get_orders_by_status(db: Session, status: str = None, skip: int = 0, limit: int = 100):
    """Get orders filtered by status for staff dashboard"""
    query = db.query(model.Order)
    
    if status:
        valid_statuses = ["pending", "confirmed", "preparing", "ready", "out_for_delivery", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        query = query.filter(model.Order.status == model.OrderStatus(status))
    
    orders = query.offset(skip).limit(limit).all()
    
    # Convert to OrderOut format
    from ..models.order_details import OrderDetail
    from ..schemas.order_details import OrderDetail as OrderDetailSchema
    
    result = []
    for order in orders:
        order_details = db.query(OrderDetail).filter(OrderDetail.order_id == order.id).all()
        
        order_data = {
            "order_number": order.order_number,
            "id": order.id,
            "status": order.status.value,
            "total_cents": order.total_cents,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "items": [OrderDetailSchema(
                id=detail.id,
                order_id=detail.order_id,
                dish_id=detail.dish_id,
                qty=detail.qty,
                unit_price_cents=detail.unit_price_cents,
                line_total_cents=detail.line_total_cents
            ) for detail in order_details],
            "created_at": order.order_date,
            "is_delivery": order.is_delivery
        }
        result.append(OrderOut.model_validate(order_data))
    
    return result
