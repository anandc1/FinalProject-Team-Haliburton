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


def test_order_placement_with_payment():
    """Test order placement with payment method selection"""
    # Create category and dish first
    category_data = {"name": "Main Course", "description": "Main dishes"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Chicken Parmesan",
        "description": "Breaded chicken with marinara",
        "price_cents": 1500,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    # Create order with payment method
    order_data = {
        "customer_name": "John Doe",
        "customer_phone": "555-1234",
        "customer_address": "123 Main St",
        "is_delivery": True,
        "payment_method": "card",
        "items": [
            {"dish_id": dish_id, "qty": 2}
        ]
    }
    
    response = client.post("/orders/guest", json=order_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify payment method is saved
    assert data["payment_method"] == "card"
    assert data["payment_status"] == "pending"
    assert data["status"] == "pending"
    assert data["is_delivery"] == True


def test_order_status_tracking():
    """Test real-time order status updates"""
    # Create order first
    category_data = {"name": "Appetizers", "description": "Starters"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Bruschetta",
        "description": "Toasted bread with tomatoes",
        "price_cents": 800,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    order_data = {
        "customer_name": "Jane Smith",
        "customer_phone": "555-5678",
        "is_delivery": False,
        "items": [{"dish_id": dish_id, "qty": 1}]
    }
    
    order_response = client.post("/orders/guest", json=order_data)
    order_number = order_response.json()["order_number"]
    
    # Update order status to confirmed
    status_update = {"status": "confirmed"}
    response = client.patch(f"/orders/{order_number}/status", json=status_update)
    assert response.status_code == 200
    
    # Update order status to preparing
    status_update = {"status": "preparing"}
    response = client.patch(f"/orders/{order_number}/status", json=status_update)
    assert response.status_code == 200
    
    # Update order status to ready
    status_update = {"status": "ready"}
    response = client.patch(f"/orders/{order_number}/status", json=status_update)
    assert response.status_code == 200
    
    # Verify final status
    order_response = client.get(f"/orders/{order_number}")
    assert order_response.json()["status"] == "ready"


def test_payment_status_updates():
    """Test payment status updates"""
    # Create order first
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
        "customer_name": "Bob Wilson",
        "customer_phone": "555-9999",
        "payment_method": "cash",
        "items": [{"dish_id": dish_id, "qty": 1}]
    }
    
    order_response = client.post("/orders/guest", json=order_data)
    order_number = order_response.json()["order_number"]
    
    # Update payment status to paid
    payment_update = {"payment_status": "paid"}
    response = client.patch(f"/orders/{order_number}/payment", json=payment_update)
    assert response.status_code == 200
    
    # Verify payment status
    order_response = client.get(f"/orders/{order_number}")
    assert order_response.json()["payment_status"] == "paid"


def test_staff_dashboard_orders():
    """Test staff dashboard order filtering"""
    # Create multiple orders with different statuses
    category_data = {"name": "Beverages", "description": "Drinks"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Coffee",
        "description": "Hot coffee",
        "price_cents": 300,
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
    
    # Get all orders
    response = client.get("/dashboard/staff/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    
    # Get pending orders only
    response = client.get("/dashboard/staff/orders?status=pending")
    assert response.status_code == 200
    data = response.json()
    for order in data:
        assert order["status"] == "pending"


def test_manager_dashboard_summary():
    """Test manager dashboard summary endpoints"""
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
    for i in range(2):
        order_data = {
            "customer_name": f"Customer {i}",
            "customer_phone": f"555-{i:04d}",
            "items": [{"dish_id": dish_id, "qty": 1}]
        }
        client.post("/orders/guest", json=order_data)
    
    # Test orders summary
    response = client.get("/dashboard/manager/orders-summary")
    assert response.status_code == 200
    data = response.json()
    assert "pending_orders" in data
    assert "preparing_orders" in data
    assert "ready_orders" in data
    assert "delivered_orders" in data
    assert "total_active_orders" in data
    
    # Test inventory summary
    response = client.get("/dashboard/manager/inventory-summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_resources" in data
    assert "low_stock_items" in data
    assert "inventory_health" in data


def test_invalid_status_update():
    """Test invalid status update handling"""
    # Create order first
    category_data = {"name": "Sides", "description": "Side dishes"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "French Fries",
        "description": "Crispy fries",
        "price_cents": 500,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    order_data = {
        "customer_name": "Test Customer",
        "customer_phone": "555-0000",
        "items": [{"dish_id": dish_id, "qty": 1}]
    }
    
    order_response = client.post("/orders/guest", json=order_data)
    order_number = order_response.json()["order_number"]
    
    # Try invalid status
    status_update = {"status": "invalid_status"}
    response = client.patch(f"/orders/{order_number}/status", json=status_update)
    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


def test_invalid_payment_status():
    """Test invalid payment status handling"""
    # Create order first
    category_data = {"name": "Salads", "description": "Fresh salads"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "Caesar Salad",
        "description": "Fresh caesar salad",
        "price_cents": 700,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    order_data = {
        "customer_name": "Test Customer",
        "customer_phone": "555-0000",
        "items": [{"dish_id": dish_id, "qty": 1}]
    }
    
    order_response = client.post("/orders/guest", json=order_data)
    order_number = order_response.json()["order_number"]
    
    # Try invalid payment status
    payment_update = {"payment_status": "invalid_status"}
    response = client.patch(f"/orders/{order_number}/payment", json=payment_update)
    assert response.status_code == 400
    assert "Invalid payment status" in response.json()["detail"]
