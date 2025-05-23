from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.general.utils.verification import verify_token
from app.pkg_smart_strip.models.DeviceRegistry import devices_registry
from app.pkg_smart_strip.models.User import User

router = APIRouter()


class DeviceQuery(BaseModel):
    id: str


class QueryRequest(BaseModel):
    devices: list[DeviceQuery]


@router.post("/smart-strip/v1.0/user/devices/query", tags=["smart_strip"])
async def devices_query(request: Request, body: QueryRequest, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")
    response_devices = []

    for requested_device in body.devices:
        device = devices_registry.get_device_by_id(requested_device.id)
        if not device:
            continue

        capabilities = []

        for cap in device.capabilities:
            cap_type = cap.type
            instance = None
            value = None

            if cap_type == "devices.capabilities.on_off":
                instance = "on"
                value = device.state.on

            elif cap_type == "devices.capabilities.range":
                instance = cap.parameters.get("instance")
                value = device.state.brightness

            elif cap_type == "devices.capabilities.mode":
                instance = cap.parameters.get("instance")
                value = device.state.program

            elif cap_type == "devices.capabilities.color_setting":
                instance = cap.parameters.get("color_model")
                value = device.state.hsv

            if not instance or not value:
                continue

            capabilities.append({
                "type": cap_type,
                "state": {
                    "instance": instance,
                    "value": value
                }
            })

        response_devices.append({
            "id": device.id,
            "capabilities": capabilities
        })

    return {
        "request_id": request_id,
        "payload": {
            "devices": response_devices
        }
    }
