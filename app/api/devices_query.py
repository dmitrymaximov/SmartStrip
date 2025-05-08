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
            continue  # или можно вернуть ошибку 404 для этого device_id

        # Собираем список capabilities с текущим состоянием
        capabilities = []
        for cap in device.capabilities:
            # определяем instance и value
            if cap.type == "devices.capabilities.on_off":
                instance = "on"
            else:
                # для range и подобных — берём instance из parameters
                instance = cap.parameters["instance"]  # e.g. "brightness"

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