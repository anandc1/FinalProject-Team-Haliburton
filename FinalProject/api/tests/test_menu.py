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


def test_create_category():
    category_data = {
        "name": "Appetizers",
        "description": "Start your meal right"
    }
    response = client.post("/menu/categories", json=category_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Appetizers"
    assert data["description"] == "Start your meal right"
    assert data["is_active"] == True


def test_create_dish():
    # First create a category
    category_data = {"name": "Main Course", "description": "Main dishes"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create dish
    dish_data = {
        "name": "Chicken Parmesan",
        "description": "Breaded chicken with marinara",
        "price_cents": 1500,
        "category_id": category_id,
        "is_active": True
    }
    response = client.post("/menu/dishes", json=dish_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chicken Parmesan"
    assert data["price_cents"] == 1500
    assert data["category_id"] == category_id


def test_list_dishes_by_category():
    # Create category
    category_data = {"name": "Desserts", "description": "Sweet treats"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create dishes
    dish1_data = {
        "name": "Chocolate Cake",
        "description": "Rich chocolate cake",
        "price_cents": 800,
        "category_id": category_id
    }
    dish2_data = {
        "name": "Ice Cream",
        "description": "Vanilla ice cream",
        "price_cents": 500,
        "category_id": category_id
    }
    client.post("/menu/dishes", json=dish1_data)
    client.post("/menu/dishes", json=dish2_data)
    
    # List dishes by category
    response = client.get(f"/menu/dishes?category_id={category_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(dish["category_id"] == category_id for dish in data)


def test_update_dish():
    # Create category and dish
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
    
    # Update dish
    update_data = {
        "name": "Espresso",
        "price_cents": 400
    }
    response = client.put(f"/menu/dishes/{dish_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Espresso"
    assert data["price_cents"] == 400


def test_delete_dish():
    # Create category and dish
    category_data = {"name": "Sides", "description": "Side dishes"}
    category_response = client.post("/menu/categories", json=category_data)
    category_id = category_response.json()["id"]
    
    dish_data = {
        "name": "French Fries",
        "description": "Crispy fries",
        "price_cents": 600,
        "category_id": category_id
    }
    dish_response = client.post("/menu/dishes", json=dish_data)
    dish_id = dish_response.json()["id"]
    
    # Delete dish
    response = client.delete(f"/menu/dishes/{dish_id}")
    assert response.status_code == 200
    
    # Verify dish is not active
    get_response = client.get(f"/menu/dishes/{dish_id}")
    assert get_response.status_code == 404
