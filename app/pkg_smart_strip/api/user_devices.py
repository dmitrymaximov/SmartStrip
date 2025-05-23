from fastapi import APIRouter, Depends, Request

from app.general.utils.verification import verify_token
from app.pkg_smart_strip.models.DeviceRegistry import devices_registry
from app.pkg_smart_strip.models.User import User

router = APIRouter()


@router.get("/smart-strip/v1.0/user/devices", tags=["smart_strip"])
async def devices(request: Request, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")
    user_id = user.user_id
    all_devices = list(devices_registry.values())

    return {
        "request_id": request_id,
        "payload": {
            "user_id": user_id,
            "devices": all_devices
        }
    }
