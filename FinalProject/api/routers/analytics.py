from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..dependencies.database import get_db
from ..controllers.analytics import (
    get_sales_analytics, get_popular_dishes, get_revenue_by_category,
    get_customer_analytics, get_promotion_analytics, get_inventory_analytics
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sales")
def get_sales_analytics_endpoint(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get sales analytics for the specified period"""
    return get_sales_analytics(db, days=days)


@router.get("/popular-dishes")
def get_popular_dishes_endpoint(
    limit: int = Query(10, description="Number of dishes to return"),
    db: Session = Depends(get_db)
):
    """Get most popular dishes based on order frequency"""
    return get_popular_dishes(db, limit=limit)


@router.get("/revenue-by-category")
def get_revenue_by_category_endpoint(db: Session = Depends(get_db)):
    """Get revenue breakdown by dish category"""
    return get_revenue_by_category(db)


@router.get("/customers")
def get_customer_analytics_endpoint(db: Session = Depends(get_db)):
    """Get customer behavior analytics"""
    return get_customer_analytics(db)


@router.get("/promotions")
def get_promotion_analytics_endpoint(db: Session = Depends(get_db)):
    """Get promotion usage analytics"""
    return get_promotion_analytics(db)


@router.get("/inventory")
def get_inventory_analytics_endpoint(db: Session = Depends(get_db)):
    """Get inventory analytics"""
    return get_inventory_analytics(db)


@router.get("/dashboard")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive analytics dashboard data"""
    return {
        "sales": get_sales_analytics(db, days=30),
        "popular_dishes": get_popular_dishes(db, limit=5),
        "revenue_by_category": get_revenue_by_category(db),
        "customers": get_customer_analytics(db),
        "promotions": get_promotion_analytics(db),
        "inventory": get_inventory_analytics(db)
    }
