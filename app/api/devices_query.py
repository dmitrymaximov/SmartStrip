from fastapi import APIRouter, Depends, Request

from pydantic import BaseModel
from typing import List, Dict

from app.models.User import User
from app.models.Device import devices_registry
from app.utils.verification import verify_token


router = APIRouter()

class QueryRequest(BaseModel):
    devices: List[Dict[str, str]]

@router.post("/smart-strip/v1.0/user/devices/query", tags=["alisa"])
async def devices_query(request: Request, body: QueryRequest, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")

    response_devices = []

    for item in body.devices:
        device = devices_registry.get(item["id"])
        if not device:
            continue

        capabilities = []

        for cap in device.capabilities:
            # определяем instance и value
            instance = None

            if cap.type == "devices.capabilities.on_off":
                instance = "on"
            elif cap.type == "devices.capabilities.range":
                instance = cap.parameters.get("instance")
            elif cap.type == "devices.capabilities.mode":
                instance = cap.parameters.get("instance")

            if not instance:
                continue

            value = device.state.get(instance)

            capabilities.append({
                "type": cap.type,
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