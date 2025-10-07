from enum import Enum
from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    IPHONE = "iphone"
    IPAD = "ipad"
    MACBOOK = "macbook"


class Device(BaseModel):
    device_type: DeviceType
    quantity: int = Field(ge=0)


class Inventory(BaseModel):
    devices: dict[DeviceType, Device] = {}


class PurchaseRequest(BaseModel):
    device_type: DeviceType
    quantity: int = Field(default=1, ge=1)


class PurchaseResponse(BaseModel):
    device_type: DeviceType
    quantity_purchased: int
    remaining_quantity: int
    message: str


class RestockRequest(BaseModel):
    device_type: DeviceType
    quantity: int = Field(ge=1)


class RestockResponse(BaseModel):
    device_type: DeviceType
    quantity_added: int
    new_quantity: int
    message: str


class InventoryResponse(BaseModel):
    devices: list[Device]