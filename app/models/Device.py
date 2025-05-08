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


def init_device_registry() -> Dict[str, Device]:
    devices_registry: Dict[str, Device] = {"smart_strip": Device(
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
                    "range": {"min": 1, "max": 100, "precision": 1}
                }
            )
        ],
        device_info=DeviceInfo(manufacturer="DIY", model="LEDv1", hw_version="1.0", sw_version="1.0"),
        state={"on": False, "brightness": 50}
    )}
    return devices_registry
