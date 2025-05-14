from fastapi import APIRouter, Depends, Request

from app.models.User import User, users_cache
from app.utils.verification import verify_token


router = APIRouter()

@router.post("/smart-strip/v1.0/user/unlink", tags=["alisa"])
async def unlink_user(request: Request, user: User = Depends(verify_token)):
    users_cache.remove_user(user)
    request_id = request.headers.get("X-Request-Id")

    return {
        "request_id": request_id
    }
