#!/usr/bin/env python3
"""
Demo Data Population Script
Populates the database with sample data for presentation demo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.dependencies.database import SessionLocal, engine, Base
from api.models.model_loader import index
from api.models import categories, dishes, orders, order_details, resources, reviews, promotions
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create comprehensive demo data for presentation"""
    
    # Clear existing database and recreate tables
    print("🗑️ Clearing existing database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Initialize database
    index()
    db = SessionLocal()
    
    try:
        print("🎯 Creating demo data for presentation...")
        
        # 1. Create Categories
        print("📋 Creating menu categories...")
        categories_data = [
            {"name": "Appetizers", "description": "Start your meal right"},
            {"name": "Main Courses", "description": "Delicious main dishes"},
            {"name": "Vegetarian", "description": "Fresh vegetarian options"},
            {"name": "Desserts", "description": "Sweet endings"},
            {"name": "Beverages", "description": "Refreshing drinks"}
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category = categories.Category(**cat_data)
            db.add(category)
            db.commit()
            db.refresh(category)
            created_categories.append(category)
            print(f"  ✅ Created category: {category.name}")
        
        # 2. Create Dishes
        print("🍽️ Creating menu dishes...")
        dishes_data = [
            {"name": "Bruschetta", "description": "Toasted bread with tomatoes", "price_cents": 800, "category_id": created_categories[0].id},
            {"name": "Caesar Salad", "description": "Fresh romaine with caesar dressing", "price_cents": 1200, "category_id": created_categories[0].id},
            {"name": "Grilled Chicken", "description": "Herb-marinated chicken breast", "price_cents": 1800, "category_id": created_categories[1].id},
            {"name": "Beef Burger", "description": "Classic beef burger with fries", "price_cents": 1600, "category_id": created_categories[1].id},
            {"name": "Vegetarian Pasta", "description": "Fresh vegetables with alfredo sauce", "price_cents": 1400, "category_id": created_categories[2].id},
            {"name": "Quinoa Bowl", "description": "Healthy quinoa with roasted vegetables", "price_cents": 1500, "category_id": created_categories[2].id},
            {"name": "Chocolate Cake", "description": "Rich chocolate layer cake", "price_cents": 900, "category_id": created_categories[3].id},
            {"name": "Ice Cream", "description": "Vanilla ice cream with toppings", "price_cents": 600, "category_id": created_categories[3].id},
            {"name": "Fresh Lemonade", "description": "Homemade lemonade", "price_cents": 400, "category_id": created_categories[4].id},
            {"name": "Coffee", "description": "Fresh brewed coffee", "price_cents": 300, "category_id": created_categories[4].id}
        ]
        
        created_dishes = []
        for dish_data in dishes_data:
            dish = dishes.Dish(**dish_data)
            db.add(dish)
            db.commit()
            db.refresh(dish)
            created_dishes.append(dish)
            print(f"  ✅ Created dish: {dish.name} - ${dish.price_cents/100:.2f}")
        
        # 3. Create Resources/Inventory
        print("📦 Creating inventory items...")
        resources_data = [
            {"name": "Chicken Breast", "description": "Fresh chicken breast", "amount": 50, "unit": "pieces"},
            {"name": "Ground Beef", "description": "Fresh ground beef", "amount": 30, "unit": "pounds"},
            {"name": "Tomatoes", "description": "Fresh tomatoes", "amount": 100, "unit": "pieces"},
            {"name": "Lettuce", "description": "Fresh romaine lettuce", "amount": 25, "unit": "heads"},
            {"name": "Bread", "description": "Fresh bread", "amount": 40, "unit": "loaves"},
            {"name": "Cheese", "description": "Cheddar cheese", "amount": 15, "unit": "pounds"},
            {"name": "Pasta", "description": "Spaghetti pasta", "amount": 20, "unit": "pounds"},
            {"name": "Coffee Beans", "description": "Premium coffee beans", "amount": 5, "unit": "pounds"},
            {"name": "Lemons", "description": "Fresh lemons", "amount": 8, "unit": "pounds"},
            {"name": "Chocolate", "description": "Dark chocolate", "amount": 3, "unit": "pounds"}
        ]
        
        created_resources = []
        for res_data in resources_data:
            resource = resources.Resource(**res_data)
            db.add(resource)
            db.commit()
            db.refresh(resource)
            created_resources.append(resource)
            print(f"  ✅ Created resource: {resource.name} - {resource.amount} {resource.unit}")
        
        # 4. Create Promotions
        print("🎉 Creating promotional codes...")
        promotions_data = [
            {"code": "WELCOME20", "description": "Welcome discount", "discount_percent": 20, "is_active": True, "expires_at": datetime.now() + timedelta(days=30)},
            {"code": "LUNCH15", "description": "Lunch special", "discount_percent": 15, "is_active": True, "expires_at": datetime.now() + timedelta(days=7)},
            {"code": "VEGGIE10", "description": "Vegetarian discount", "discount_percent": 10, "is_active": True, "expires_at": datetime.now() + timedelta(days=14)}
        ]
        
        created_promotions = []
        for promo_data in promotions_data:
            promotion = promotions.Promotion(**promo_data)
            db.add(promotion)
            db.commit()
            db.refresh(promotion)
            created_promotions.append(promotion)
            print(f"  ✅ Created promotion: {promotion.code} - {promotion.discount_percent}% off")
        
        # 5. Create Sample Orders
        print("📝 Creating sample orders...")
        
        # Create orders over the past week for analytics
        for i in range(15):
            order_date = datetime.now() - timedelta(days=random.randint(0, 7))
            
            # Generate order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
            
            # Create order
            order = orders.Order(
                order_number=order_number,
                customer_name=f"Customer {i+1}",
                customer_phone=f"555-{1000+i:04d}",
                description=f"Sample order {i+1}",
                total_cents=random.randint(2000, 5000),
                status=random.choice(["PENDING", "CONFIRMED", "PREPARING", "READY", "DELIVERED"]),
                payment_status=random.choice(["pending", "paid"]),
                payment_method=random.choice(["cash", "card", "online"]),
                order_date=order_date
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            
            # Create order details
            num_items = random.randint(1, 3)
            for j in range(num_items):
                dish = random.choice(created_dishes)
                qty = random.randint(1, 3)
                order_detail = order_details.OrderDetail(
                    order_id=order.id,
                    dish_id=dish.id,
                    qty=qty,
                    unit_price_cents=dish.price_cents,
                    line_total_cents=dish.price_cents * qty
                )
                db.add(order_detail)
            
            print(f"  ✅ Created order: {order.customer_name} - ${order.total_cents/100:.2f}")
        
        # 6. Create Reviews
        print("⭐ Creating customer reviews...")
        review_texts = [
            "Amazing food! Will definitely order again.",
            "Great service and delicious food.",
            "The vegetarian options are fantastic!",
            "Quick delivery and hot food.",
            "Love the new menu items!",
            "Excellent quality for the price.",
            "The staff is very friendly.",
            "Perfect for family dinner.",
            "Highly recommend this place!",
            "Best restaurant in the area!"
        ]
        
        for i in range(10):
            # Get a random order for the review
            order = db.query(orders.Order).offset(i % 15).first()
            if order:
                review = reviews.Review(
                    order_number=order.order_number,
                    customer_name=f"Reviewer {i+1}",
                    rating=random.randint(3, 5),
                    review_text=random.choice(review_texts),
                    is_approved=True
                )
                db.add(review)
                print(f"  ✅ Created review: {review.customer_name} - {review.rating} stars")
        
        db.commit()
        
        print("\n🎉 Demo data creation completed successfully!")
        print("\n📊 Demo Data Summary:")
        print(f"  • {len(created_categories)} Categories")
        print(f"  • {len(created_dishes)} Dishes")
        print(f"  • {len(created_resources)} Inventory Items")
        print(f"  • {len(created_promotions)} Promotional Codes")
        print(f"  • 15 Sample Orders")
        print(f"  • 10 Customer Reviews")
        
        print("\n🚀 Your API is ready for demo!")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🔗 Base URL: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
