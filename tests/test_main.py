import pytest
from fastapi.testclient import TestClient
from apple_store.main import app, inventory
from apple_store.utils import initialize_inventory


@pytest.fixture(autouse=True)
def reset_inventory():
    global inventory
    from apple_store import main
    main.inventory = initialize_inventory()
    yield


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Apple Store API"}


def test_get_devices():
    response = client.get("/devices")
    assert response.status_code == 200
    data = response.json()
    assert "devices" in data
    assert len(data["devices"]) == 3
    
    device_types = {device["device_type"] for device in data["devices"]}
    assert device_types == {"iphone", "ipad", "macbook"}


def test_create_purchase_success():
    response = client.post("/devices/purchases", json={
        "device_type": "iphone",
        "quantity": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert data["device_type"] == "iphone"
    assert data["quantity_purchased"] == 5
    assert data["remaining_quantity"] == 45


def test_create_purchase_default_quantity():
    response = client.post("/devices/purchases", json={
        "device_type": "ipad"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["quantity_purchased"] == 1
    assert data["remaining_quantity"] == 29


def test_create_purchase_insufficient_stock():
    response = client.post("/devices/purchases", json={
        "device_type": "macbook",
        "quantity": 100
    })
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_create_purchase_invalid_type():
    response = client.post("/devices/purchases", json={
        "device_type": "airpods",
        "quantity": 1
    })
    assert response.status_code == 422


def test_create_restock_success():
    response = client.post("/devices/restocks", json={
        "device_type": "iphone",
        "quantity": 25
    })
    assert response.status_code == 200
    data = response.json()
    assert data["device_type"] == "iphone"
    assert data["quantity_added"] == 25
    assert data["new_quantity"] == 75


def test_restock_then_purchase():
    restock_response = client.post("/devices/restocks", json={
        "device_type": "ipad",
        "quantity": 20
    })
    assert restock_response.status_code == 200
    assert restock_response.json()["new_quantity"] == 50
    
    purchase_response = client.post("/devices/purchases", json={
        "device_type": "ipad",
        "quantity": 10
    })
    assert purchase_response.status_code == 200
    assert purchase_response.json()["remaining_quantity"] == 40


def test_purchase_all_stock():
    response = client.post("/devices/purchases", json={
        "device_type": "macbook",
        "quantity": 20
    })
    assert response.status_code == 200
    data = response.json()
    assert data["remaining_quantity"] == 0
    
    devices_response = client.get("/devices")
    devices = devices_response.json()["devices"]
    macbook = next(d for d in devices if d["device_type"] == "macbook")
    assert macbook["quantity"] == 0


def test_purchase_from_empty_stock():
    client.post("/devices/purchases", json={
        "device_type": "ipad",
        "quantity": 30
    })
    
    response = client.post("/devices/purchases", json={
        "device_type": "ipad",
        "quantity": 1
    })
    assert response.status_code == 400


def test_multiple_operations():
    client.post("/devices/purchases", json={"device_type": "iphone", "quantity": 10})
    client.post("/devices/restocks", json={"device_type": "iphone", "quantity": 15})
    client.post("/devices/purchases", json={"device_type": "iphone", "quantity": 5})
    
    devices_response = client.get("/devices")
    devices = devices_response.json()["devices"]
    iphone = next(d for d in devices if d["device_type"] == "iphone")
    assert iphone["quantity"] == 50