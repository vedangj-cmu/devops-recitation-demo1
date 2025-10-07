from apple_store.models import Device, DeviceType, Inventory


def initialize_inventory() -> Inventory:
    return Inventory(
        devices={
            DeviceType.IPHONE: Device(device_type=DeviceType.IPHONE, quantity=50),
            DeviceType.IPAD: Device(device_type=DeviceType.IPAD, quantity=30),
            DeviceType.MACBOOK: Device(device_type=DeviceType.MACBOOK, quantity=20),
        }
    )