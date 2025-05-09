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
        return self.state["brightness"]

    def update_brightness(self, value: Any):
        return self.state["brightness"]

    def get_mode(self):
        return self.state["program"]

    def update_mode(self, value: StripMode):
        self.state["program"] = value

    def get_color(self):
        return self.state["hsv"]

    def update_color(self, value: Any):
        self.state["hsv"] = value



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
                    "instance": "program",
                    "modes": [
                        {"value": "one"},
                        {"value": "two"},
                        {"value": "three"},
                        {"value": "four"},
                        {"value": "five"},
                        {"value": "six"},
                    ]
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
        device_info=DeviceInfo(manufacturer="Maxs", model="Strip", hw_version="1.0", sw_version="1.0"),
        state={
            "on": True,
            "brightness": 100,
            "program": "one",
            "hsv": {
                "h": 240,
                "s": 100,
                "v": 100
            }
        }
    )}
    return devices


devices_registry: Dict[str, Device] = init_device_registry()