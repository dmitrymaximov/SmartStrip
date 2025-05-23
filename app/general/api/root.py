from fastapi import APIRouter, Depends

from app.general.utils.verification import verify_basic_auth


router = APIRouter()

@router.get("/", tags=["system"])
async def root(auth: bool = Depends(verify_basic_auth)):
    return {
        "message": "Hi"
    }
