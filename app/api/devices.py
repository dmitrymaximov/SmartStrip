from fastapi import APIRouter, Depends, Request

from app.models.User import User
from app.models.Device import devices_registry
from app.utils.verification import verify_token


router = APIRouter()

@router.get("/smart-strip/v1.0/user/devices", tags=["alisa"])
async def devices(request: Request, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")
    user_id = user.user_id
    all_devices = list(devices_registry.values())

    print(f"/smart-strip/v1.0/user/devices:")
    print(f"---request_id: {request_id}")
    print(f"---user_id: {user_id}")
    print(f"---devices: {all_devices}")

    return {
        "request_id": request_id,
        "payload": {
            "user_id": user_id,
            "devices": all_devices
        }
    }