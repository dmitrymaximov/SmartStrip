from fastapi import APIRouter, Depends

from app.models.User import users_cache
from app.utils.verification import verify_api_key


router = APIRouter()

@router.get("/users", tags=["general"])
async def users(api_key: str = Depends(verify_api_key)) -> list[str]:
    return users_cache.get_users()
