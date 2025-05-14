from fastapi import APIRouter, Depends, Request

from pydantic import BaseModel

from app.models.User import User
from app.models.Device import devices_registry
from app.utils.verification import verify_token


router = APIRouter()

class DeviceQuery(BaseModel):
    id: str


class QueryRequest(BaseModel):
    devices: list[DeviceQuery]


@router.post("/smart-strip/v1.0/user/devices/query", tags=["alisa"])
async def devices_query(request: Request, body: QueryRequest, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")
    response_devices = []

    for requested_device in body.devices:
        device = devices_registry.get(requested_device.id)
        if not device:
            continue

        capabilities = []

        for cap in device.capabilities:
            cap_type = cap.type
            instance = None

            if cap_type == "devices.capabilities.on_off":
                instance = "on"

            elif cap_type == "devices.capabilities.range":
                instance = cap.parameters.get("instance")

            elif cap_type == "devices.capabilities.mode":
                instance = cap.parameters.get("instance")

            elif cap_type == "devices.capabilities.color_setting":
                instance = cap.parameters.get("color_model")

            if not instance:
                continue

            value = device.state.get(instance)

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