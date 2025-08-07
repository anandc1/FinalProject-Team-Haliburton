from fastapi.testclient import TestClient
from ..controllers import orders as controller
from ..main import app
import pytest
from ..models import orders as model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..dependencies.database import Base, get_db

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


def test_create_order(db_session):
    # Create a sample order
    order_data = {
        "customer_name": "John Doe",
        "description": "Test order"
    }

    order_object = model.Order(**order_data)

    # Call the create function
    created_order = controller.create(db_session, order_object)

    # Assertions
    assert created_order is not None
    assert created_order.customer_name == "John Doe"
    assert created_order.description == "Test order"


def test_create_guest_order():
    # Create category and dishes first
    category_data = {"name": "Main Course", "description": "Main dishes"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish1_data = {
        "name": "Chicken Parmesan",
        "description": "Breaded chicken with marinara",
        "price_cents": 1500,
        "category_id": category_id
    }
    dish2_data = {
        "name": "Pasta Carbonara",
        "description": "Creamy pasta with bacon",
        "price_cents": 1200,
        "category_id": category_id
    }
    
    dish1_response = client.post("/menu/dishes", json=dish1_data)
    dish2_response = client.post("/menu/dishes", json=dish2_data)
    dish1_id = dish1_response.json()["id"]
    dish2_id = dish2_response.json()["id"]
    
    # Create guest order
    order_data = {
        "customer_name": "Jane Smith",
        "customer_phone": "555-1234",
        "customer_address": "123 Main St",
        "is_delivery": True,
        "items": [
            {"dish_id": dish1_id, "qty": 2},
            {"dish_id": dish2_id, "qty": 1}
        ]
    }
    
    response = client.post("/orders/guest", json=order_data)
    assert response.status_code == 200
    data = response.json()
    
    # Assert order_number is present
    assert "order_number" in data
    assert len(data["order_number"]) > 0
    
    # Assert totals match sum of line totals
    expected_total = (1500 * 2) + (1200 * 1)  # 4200 cents
    assert data["total_cents"] == expected_total
    
    # Verify items
    assert len(data["items"]) == 2
    assert data["items"][0]["qty"] == 2
    assert data["items"][0]["unit_price_cents"] == 1500
    assert data["items"][0]["line_total_cents"] == 3000
    assert data["items"][1]["qty"] == 1
    assert data["items"][1]["unit_price_cents"] == 1200
    assert data["items"][1]["line_total_cents"] == 1200
    
    # Fetch by order_number and verify
    order_number = data["order_number"]
    fetch_response = client.get(f"/orders/{order_number}")
    assert fetch_response.status_code == 200
    fetch_data = fetch_response.json()
    assert fetch_data["order_number"] == order_number
    assert fetch_data["total_cents"] == expected_total
    assert len(fetch_data["items"]) == 2
