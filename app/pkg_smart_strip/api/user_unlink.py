from fastapi import APIRouter, Depends, Request

from app.general.utils.verification import verify_token
from app.pkg_smart_strip.models.User import User
from app.pkg_smart_strip.models.UserRegistry import users_cache

router = APIRouter()


@router.post("/smart-strip/v1.0/user/unlink", tags=["smart_strip"])
async def unlink_user(request: Request, user: User = Depends(verify_token)):
    users_cache.remove_user(user)
    request_id = request.headers.get("X-Request-Id")

    return {
        "request_id": request_id
    }
