from fastapi import FastAPI, HTTPException
from apple_store.models import (
    PurchaseRequest,
    PurchaseResponse,
    RestockRequest,
    RestockResponse,
    InventoryResponse,
    Device,
)
from apple_store.utils import initialize_inventory

app = FastAPI(title="Apple Store API")

inventory = initialize_inventory()


@app.get("/")
def root():
    return {"message": "Apple Store API"}


@app.get("/devices", response_model=InventoryResponse)
def get_devices():
    devices_list = list(inventory.devices.values())
    return InventoryResponse(devices=devices_list)


@app.post("/devices/purchases", response_model=PurchaseResponse)
def create_purchase(request: PurchaseRequest):
    device = inventory.devices.get(request.device_type)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device type not found")
    
    if device.quantity < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {device.quantity}, Requested: {request.quantity}"
        )
    
    device.quantity -= request.quantity
    
    return PurchaseResponse(
        device_type=request.device_type,
        quantity_purchased=request.quantity,
        remaining_quantity=device.quantity,
        message=f"Successfully purchased {request.quantity} {request.device_type.value}(s)"
    )


@app.post("/devices/restocks", response_model=RestockResponse)
def create_restock(request: RestockRequest):
    device = inventory.devices.get(request.device_type)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device type not found")
    
    device.quantity = request.quantity
    
    return RestockResponse(
        device_type=request.device_type,
        quantity_added=request.quantity,
        new_quantity=device.quantity,
        message=f"Successfully restocked {request.quantity} {request.device_type.value}(s)"
    )