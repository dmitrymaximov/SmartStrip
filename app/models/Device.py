from fastapi import WebSocket

from pydantic import BaseModel, Field
from typing import Any, Literal, TypeVar, Generic


STATE = TypeVar("STATE", bound=BaseModel)


class Capability(BaseModel):
    type: str
    retrievable: bool = False
    parameters: dict[str, Any] | None = None


class DeviceInfo(BaseModel):
    manufacturer: str | None = None
    model: str | None = None
    hw_version: str | None = None
    sw_version: str | None = None


class HSVColor(BaseModel):
    h: int
    s: int
    v: int


class SmartStripState(BaseModel):
    on: bool = True
    brightness: int = 100
    program: Literal["one", "two", "three", "four", "five"] = "one"
    hsv: HSVColor = HSVColor(h=240, s=100, v=100)


class Device(BaseModel, Generic[STATE]):
    id: str
    name: str
    type: str = Field(..., alias="device_type")
    capabilities: list[Capability] = []
    device_info: DeviceInfo
    state: STATE
    connection: WebSocket | None = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class SmartStripDevice(Device[SmartStripState]):
    def __init__(self, device_id: str, connection: WebSocket | None = None):
        super().__init__(
            id=device_id,
            name="Умная лента",
            device_type="devices.types.light",
            capabilities=[
                Capability(
                    type="devices.capabilities.on_off",
                    retrievable=True,
                    parameters={}
                ),
                Capability(
                    type="devices.capabilities.range",
                    retrievable=True,
                    parameters={
                        "instance": "brightness",
                        "unit": "unit.percent",
                        "range": {
                            "min": 0,
                            "max": 100,
                            "precision": 1
                        }
                    }
                ),
                Capability(
                    type="devices.capabilities.mode",
                    retrievable=True,
                    parameters={
                        "instance": "program",
                        "modes": [{"value": mode} for mode in ["one", "two", "three", "four", "five"]]
                    }
                ),
                Capability(
                    type="devices.capabilities.color_setting",
                    retrievable=True,
                    parameters={
                        "color_model": "hsv"
                    }
                )
            ],
            device_info=DeviceInfo(
                manufacturer="Maxs",
                model="Strip",
                hw_version="1.0",
                sw_version="1.0"
            ),
            state=SmartStripState(),
            connection=connection
        )


class DeviceRegistry:
    devices: list[SmartStripDevice] = list()

    def add_device(self, device: SmartStripDevice):
        self.devices.append(device)

    def get_device_by_id(self, device_id: str) -> SmartStripDevice | None:
        return next((device for device in self.devices if device.id == device_id), None)

    def get_devices(self) -> list[str]:
        return [device.id for device in self.devices]

    def remove_device(self, device):
        if device in self.devices:
            self.devices.remove(device)

    def remove_device_by_id(self, device_id: str):
        device = self.get_device_by_id(device_id)

        if device:
            self.devices.remove(device)

    def init_test_device(self, device_id="test"):
        device = SmartStripDevice(device_id)
        self.add_device(device)


devices_registry = DeviceRegistry()
devices_registry.init_test_device("test_1")
devices_registry.init_test_device("test_2")

