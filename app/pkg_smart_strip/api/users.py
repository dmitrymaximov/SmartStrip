from fastapi import APIRouter, Depends

from app.general.utils.verification import verify_api_key
from app.pkg_smart_strip.models.UserRegistry import users_cache

router = APIRouter()


@router.get("/smart-strip/v1.0/users", tags=["smart_strip"])
async def users(api_key: str = Depends(verify_api_key)) -> list[str]:
    return users_cache.get_users()
