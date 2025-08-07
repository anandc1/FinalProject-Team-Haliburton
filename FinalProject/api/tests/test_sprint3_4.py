import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..dependencies.database import Base, get_db
from ..main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_review():
    """Test creating a customer review"""
    # Create order first
    category_data = {"name": "Main Course", "description": "Main dishes"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Steak",
        "description": "Grilled steak",
        "price_cents": 2500,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    order_data = {
        "customer_name": "John Doe",
        "customer_phone": "555-1234",
        "items": [{"dish_id": dish_id, "qty": 1}]
    }
    order_response = client.post("/orders/guest", json=order_data)
    order_number = order_response.json()["order_number"]
    
    # Create review
    review_data = {
        "order_number": order_number,
        "customer_name": "John Doe",
        "rating": 5,
        "review_text": "Excellent food and service!"
    }
    
    response = client.post("/reviews/", json=review_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["rating"] == 5
    assert data["review_text"] == "Excellent food and service!"
    assert data["is_approved"] == False


def test_create_promotion():
    """Test creating a promotion code"""
    promotion_data = {
        "code": "SAVE20",
        "description": "20% off all orders",
        "discount_percent": 20,
        "min_order_amount_cents": 1000,
        "max_discount_cents": 5000
    }
    
    response = client.post("/promotions/", json=promotion_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["code"] == "SAVE20"
    assert data["discount_percent"] == 20
    assert data["is_active"] == True


def test_apply_promotion():
    """Test applying a promotion code"""
    # Create promotion first
    promotion_data = {
        "code": "SAVE10",
        "description": "10% off",
        "discount_percent": 10,
        "min_order_amount_cents": 500
    }
    client.post("/promotions/", json=promotion_data)
    
    # Apply promotion
    apply_data = {
        "code": "SAVE10",
        "order_total_cents": 1000
    }
    
    response = client.post("/promotions/apply", json=apply_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["promotion_code"] == "SAVE10"
    assert data["discount_percent"] == 10
    assert data["discount_amount_cents"] == 100
    assert data["final_total_cents"] == 900


def test_analytics_sales():
    """Test sales analytics endpoint"""
    # Create some orders first
    category_data = {"name": "Pizza", "description": "Italian pizza"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Margherita Pizza",
        "description": "Classic margherita",
        "price_cents": 1200,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    # Create orders
    for i in range(3):
        order_data = {
            "customer_name": f"Customer {i}",
            "customer_phone": f"555-{i:04d}",
            "items": [{"dish_id": dish_id, "qty": 1}]
        }
        client.post("/orders/guest", json=order_data)
    
    response = client.get("/analytics/sales")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_orders" in data
    assert "total_revenue_cents" in data
    assert "average_order_value_cents" in data


def test_analytics_popular_dishes():
    """Test popular dishes analytics"""
    # Create dishes and orders first
    category_data = {"name": "Burgers", "description": "Burgers"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Cheeseburger",
        "description": "Classic cheeseburger",
        "price_cents": 800,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    # Create orders
    order_data = {
        "customer_name": "Test Customer",
        "customer_phone": "555-0000",
        "items": [{"dish_id": dish_id, "qty": 2}]
    }
    client.post("/orders/guest", json=order_data)
    
    response = client.get("/analytics/popular-dishes")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) > 0
    assert "dish_name" in data[0]
    assert "total_quantity" in data[0]


def test_analytics_dashboard():
    """Test comprehensive analytics dashboard"""
    response = client.get("/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    
    assert "sales" in data
    assert "popular_dishes" in data
    assert "revenue_by_category" in data
    assert "customers" in data
    assert "promotions" in data
    assert "inventory" in data


def test_review_statistics():
    """Test review statistics endpoint"""
    # Create review first
    category_data = {"name": "Desserts", "description": "Sweet treats"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Chocolate Cake",
        "description": "Rich chocolate cake",
        "price_cents": 600,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    order_data = {
        "customer_name": "Jane Smith",
        "customer_phone": "555-5678",
        "items": [{"dish_id": dish_id, "qty": 1}]
    }
    order_response = client.post("/orders/guest", json=order_data)
    order_number = order_response.json()["order_number"]
    
    review_data = {
        "order_number": order_number,
        "customer_name": "Jane Smith",
        "rating": 4,
        "review_text": "Great dessert!"
    }
    client.post("/reviews/", json=review_data)
    
    response = client.get("/reviews/stats/summary")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_reviews" in data
    assert "average_rating" in data
    assert "rating_distribution" in data


def test_promotion_validation():
    """Test promotion code validation"""
    # Create promotion
    promotion_data = {
        "code": "VALID20",
        "description": "Valid promotion",
        "discount_percent": 20
    }
    client.post("/promotions/", json=promotion_data)
    
    # Test valid code
    response = client.get("/promotions/validate/VALID20")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True
    
    # Test invalid code
    response = client.get("/promotions/validate/INVALID")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == False
