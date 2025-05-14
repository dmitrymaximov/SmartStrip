from fastapi import APIRouter, Depends

from app.models.Device import devices_registry
from app.utils.verification import verify_api_key


router = APIRouter()

@router.get("/devices", tags=["general"])
async def devices(api_key: str = Depends(verify_api_key)) -> list[str]:
    return devices_registry.get_devices()
