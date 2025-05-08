from pydantic import BaseModel, Field
from typing import Any, Dict, List

from app.models.Enums import StripColor, StripMode, StripState, StripTest



class Capability(BaseModel):
    type: str
    retrievable: bool = False
    parameters: Dict[str, Any] | None = None


class DeviceInfo(BaseModel):
    manufacturer: str | None = None
    model: str | None = None
    hw_version: str | None = None
    sw_version: str | None = None


class Device(BaseModel):
    id: str
    name: str
    type: str = Field(..., alias="device_type")
    capabilities: List[Capability] = []
    properties: List[Any] = []
    device_info: DeviceInfo
    # Здесь храним текущее состояние — ключи совпадают с instance в capabilities
    state: Dict[str, Any] = Field(default_factory=dict)

    def get_state(self):
        return self.state["on"]

    def update_state(self, value: bool):
        self.state["on"] = value

    def get_brightness(self):
        pass

    def update_brightness(self, value: Any):
        pass

    def get_mode(self):
        pass

    def update_mode(self, value: Any):
        pass

    def get_color(self):
        pass

    def update_color(self, value: Any):
        pass



def init_device_registry() -> Dict[str, Device]:
    devices: Dict[str, Device] = {"smart_strip": Device(
        id="smart_strip",
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
                    "instance": "scene",
                    "modes": [
                        {"value": "static", "name": {"ru": "Статичный"}},
                        {"value": "rainbow", "name": {"ru": "Радуга"}},
                        {"value": "police", "name": {"ru": "Полиция"}}
                    ]
                }
            )
        ],
        device_info=DeviceInfo(manufacturer="Maxs", model="Strip", hw_version="1.0", sw_version="1.0"),
        state={
            "on": True,
            "brightness": 100,
            "scene": "static"
        }
    )}
    return devices


devices_registry: Dict[str, Device] = init_device_registry()