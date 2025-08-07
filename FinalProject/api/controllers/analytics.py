from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from ..models.orders import Order, OrderStatus
from ..models.dishes import Dish
from ..models.reviews import Review
from ..models.promotions import Promotion


def get_sales_analytics(db: Session, days: int = 30):
    """Get sales analytics for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get orders in date range
    orders = db.query(Order).filter(
        and_(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        )
    ).all()
    
    total_orders = len(orders)
    total_revenue = sum(order.total_cents for order in orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Orders by status
    status_counts = {}
    for status in OrderStatus:
        count = len([o for o in orders if o.status == status])
        status_counts[status.value] = count
    
    return {
        "period_days": days,
        "total_orders": total_orders,
        "total_revenue_cents": total_revenue,
        "total_revenue_dollars": total_revenue / 100,
        "average_order_value_cents": avg_order_value,
        "average_order_value_dollars": avg_order_value / 100,
        "orders_by_status": status_counts
    }


def get_popular_dishes(db: Session, limit: int = 10):
    """Get most popular dishes based on order frequency"""
    from ..models.order_details import OrderDetail
    
    dish_orders = db.query(
        Dish.id,
        Dish.name,
        func.sum(OrderDetail.qty).label('total_quantity'),
        func.count(OrderDetail.order_id.distinct()).label('order_count')
    ).join(OrderDetail).filter(
        Dish.is_active == True
    ).group_by(Dish.id, Dish.name).order_by(
        func.sum(OrderDetail.qty).desc()
    ).limit(limit).all()
    
    return [
        {
            "dish_id": dish.id,
            "dish_name": dish.name,
            "total_quantity": int(dish.total_quantity),
            "order_count": int(dish.order_count),
            "average_quantity": round(dish.total_quantity / dish.order_count, 2) if dish.order_count > 0 else 0
        }
        for dish in dish_orders
    ]


def get_revenue_by_category(db: Session):
    """Get revenue breakdown by dish category"""
    from ..models.order_details import OrderDetail
    from ..models.categories import Category
    
    category_revenue = db.query(
        Category.id,
        Category.name,
        func.sum(OrderDetail.line_total_cents).label('total_revenue')
    ).join(Dish).join(OrderDetail).filter(
        Category.is_active == True,
        Dish.is_active == True
    ).group_by(Category.id, Category.name).order_by(
        func.sum(OrderDetail.line_total_cents).desc()
    ).all()
    
    return [
        {
            "category_id": cat.id,
            "category_name": cat.name,
            "total_revenue_cents": int(cat.total_revenue),
            "total_revenue_dollars": round(cat.total_revenue / 100, 2)
        }
        for cat in category_revenue
    ]


def get_customer_analytics(db: Session):
    """Get customer behavior analytics"""
    # Total unique customers
    unique_customers = db.query(func.count(func.distinct(Order.customer_name))).scalar()
    
    # Average orders per customer
    total_orders = db.query(func.count(Order.id)).scalar()
    avg_orders_per_customer = total_orders / unique_customers if unique_customers > 0 else 0
    
    # Delivery vs takeout ratio
    delivery_orders = db.query(func.count(Order.id)).filter(Order.is_delivery == True).scalar()
    takeout_orders = db.query(func.count(Order.id)).filter(Order.is_delivery == False).scalar()
    
    return {
        "unique_customers": unique_customers,
        "total_orders": total_orders,
        "average_orders_per_customer": round(avg_orders_per_customer, 2),
        "delivery_orders": delivery_orders,
        "takeout_orders": takeout_orders,
        "delivery_percentage": round((delivery_orders / total_orders) * 100, 2) if total_orders > 0 else 0
    }


def get_promotion_analytics(db: Session):
    """Get promotion usage analytics"""
    active_promotions = db.query(Promotion).filter(Promotion.is_active == True).all()
    
    total_promotions = len(active_promotions)
    total_usage = sum(promo.times_used for promo in active_promotions)
    
    return {
        "active_promotions": total_promotions,
        "total_usage": total_usage,
        "average_usage_per_promotion": round(total_usage / total_promotions, 2) if total_promotions > 0 else 0,
        "promotions": [
            {
                "code": promo.code,
                "description": promo.description,
                "times_used": promo.times_used,
                "usage_limit": promo.usage_limit
            }
            for promo in active_promotions
        ]
    }


def get_inventory_analytics(db: Session):
    """Get inventory analytics"""
    from ..models.resources import Resource
    
    resources = db.query(Resource).filter(Resource.is_active == True).all()
    
    total_resources = len(resources)
    low_stock_resources = [r for r in resources if r.amount <= 10]
    
    return {
        "total_resources": total_resources,
        "low_stock_items": len(low_stock_resources),
        "low_stock_percentage": round((len(low_stock_resources) / total_resources) * 100, 2) if total_resources > 0 else 0,
        "low_stock_items": [
            {
                "name": resource.name,
                "current_amount": resource.amount,
                "unit": resource.unit
            }
            for resource in low_stock_resources
        ]
    }
