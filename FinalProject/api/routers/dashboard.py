from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies.database import get_db
from ..controllers import orders as order_controller
from ..controllers import menu as menu_controller
from ..controllers import resources as resource_controller
from ..schemas.orders import OrderOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/staff/orders", response_model=List[OrderOut])
def get_staff_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get orders for staff dashboard with optional status filtering"""
    return order_controller.get_orders_by_status(db=db, status=status, skip=skip, limit=limit)


@router.get("/staff/low-stock")
def get_low_stock_alerts(
    threshold: int = Query(10, description="Stock level threshold"),
    db: Session = Depends(get_db)
):
    """Get low stock alerts for staff dashboard"""
    return resource_controller.get_low_stock_resources(db=db, threshold=threshold)


@router.get("/staff/menu-stats")
def get_menu_statistics(db: Session = Depends(get_db)):
    """Get menu statistics for staff dashboard"""
    # Get active categories count
    categories = menu_controller.get_categories(db=db)
    active_categories = len(categories)
    
    # Get active dishes count
    dishes = menu_controller.get_dishes(db=db)
    active_dishes = len(dishes)
    
    return {
        "active_categories": active_categories,
        "active_dishes": active_dishes,
        "total_menu_items": active_categories + active_dishes
    }


@router.get("/manager/orders-summary")
def get_orders_summary(
    db: Session = Depends(get_db)
):
    """Get orders summary for manager dashboard"""
    # Get orders by status
    pending_orders = order_controller.get_orders_by_status(db=db, status="pending")
    preparing_orders = order_controller.get_orders_by_status(db=db, status="preparing")
    ready_orders = order_controller.get_orders_by_status(db=db, status="ready")
    delivered_orders = order_controller.get_orders_by_status(db=db, status="delivered")
    
    return {
        "pending_orders": len(pending_orders),
        "preparing_orders": len(preparing_orders),
        "ready_orders": len(ready_orders),
        "delivered_orders": len(delivered_orders),
        "total_active_orders": len(pending_orders) + len(preparing_orders) + len(ready_orders)
    }


@router.get("/manager/inventory-summary")
def get_inventory_summary(
    db: Session = Depends(get_db)
):
    """Get inventory summary for manager dashboard"""
    # Get all resources
    resources = resource_controller.get_resources(db=db)
    
    total_resources = len(resources)
    low_stock_resources = resource_controller.get_low_stock_resources(db=db, threshold=10)
    
    return {
        "total_resources": total_resources,
        "low_stock_items": len(low_stock_resources),
        "inventory_health": "good" if len(low_stock_resources) < 3 else "warning"
    }
