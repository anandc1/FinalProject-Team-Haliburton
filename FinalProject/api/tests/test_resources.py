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


def test_create_resource():
    resource_data = {
        "name": "Tomatoes",
        "description": "Fresh tomatoes for cooking",
        "amount": 50,
        "unit": "kg",
        "is_active": True
    }
    response = client.post("/resources/", json=resource_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tomatoes"
    assert data["amount"] == 50
    assert data["unit"] == "kg"
    assert data["is_active"] == True


def test_get_resource():
    # Create resource first
    resource_data = {
        "name": "Cheese",
        "description": "Mozzarella cheese",
        "amount": 25,
        "unit": "kg"
    }
    create_response = client.post("/resources/", json=resource_data)
    resource_id = create_response.json()["id"]
    
    # Get resource
    response = client.get(f"/resources/{resource_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cheese"
    assert data["amount"] == 25


def test_update_resource():
    # Create resource first
    resource_data = {
        "name": "Flour",
        "description": "All-purpose flour",
        "amount": 100,
        "unit": "kg"
    }
    create_response = client.post("/resources/", json=resource_data)
    resource_id = create_response.json()["id"]
    
    # Update resource
    update_data = {
        "amount": 75,
        "description": "Updated flour description"
    }
    response = client.put(f"/resources/{resource_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 75
    assert data["description"] == "Updated flour description"


def test_delete_resource():
    # Create resource first
    resource_data = {
        "name": "Oil",
        "description": "Cooking oil",
        "amount": 30,
        "unit": "liters"
    }
    create_response = client.post("/resources/", json=resource_data)
    resource_id = create_response.json()["id"]
    
    # Delete resource
    response = client.delete(f"/resources/{resource_id}")
    assert response.status_code == 200
    
    # Verify resource is not active
    get_response = client.get(f"/resources/{resource_id}")
    assert get_response.status_code == 404


def test_update_resource_amount():
    # Create resource first
    resource_data = {
        "name": "Chicken",
        "description": "Fresh chicken breast",
        "amount": 20,
        "unit": "kg"
    }
    create_response = client.post("/resources/", json=resource_data)
    resource_id = create_response.json()["id"]
    
    # Add stock
    response = client.patch(f"/resources/{resource_id}/amount?amount_change=10")
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 30  # 20 + 10
    
    # Subtract stock
    response = client.patch(f"/resources/{resource_id}/amount?amount_change=-5")
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 25  # 30 - 5


def test_update_resource_amount_insufficient():
    # Create resource first
    resource_data = {
        "name": "Beef",
        "description": "Ground beef",
        "amount": 10,
        "unit": "kg"
    }
    create_response = client.post("/resources/", json=resource_data)
    resource_id = create_response.json()["id"]
    
    # Try to subtract more than available
    response = client.patch(f"/resources/{resource_id}/amount?amount_change=-15")
    assert response.status_code == 400
    assert "Insufficient inventory" in response.json()["detail"]


def test_get_low_stock_resources():
    # Create resources with different amounts
    resources_data = [
        {"name": "High Stock", "amount": 50, "unit": "kg"},
        {"name": "Low Stock", "amount": 5, "unit": "kg"},
        {"name": "Medium Stock", "amount": 15, "unit": "kg"}
    ]
    
    for resource_data in resources_data:
        client.post("/resources/", json=resource_data)
    
    # Get low stock resources (threshold = 10)
    response = client.get("/resources/low-stock/?threshold=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Low Stock (5) and Medium Stock (15)
    
    # Verify all returned resources have amount <= threshold
    for resource in data:
        assert resource["amount"] <= 10


def test_list_resources():
    # Create multiple resources
    resources_data = [
        {"name": "Resource 1", "amount": 10, "unit": "pieces"},
        {"name": "Resource 2", "amount": 20, "unit": "kg"},
        {"name": "Resource 3", "amount": 30, "unit": "liters"}
    ]
    
    for resource_data in resources_data:
        client.post("/resources/", json=resource_data)
    
    # List all resources
    response = client.get("/resources/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Test pagination
    response = client.get("/resources/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
