from fastapi import APIRouter, Depends

from app.general.utils.verification import verify_api_key
from app.pkg_smart_strip.models.DeviceRegistry import devices_registry

router = APIRouter()


@router.get("/smart-strip/v1.0/devices", tags=["smart_strip"])
async def devices(api_key: str = Depends(verify_api_key)) -> list[str]:
    return devices_registry.get_devices()
