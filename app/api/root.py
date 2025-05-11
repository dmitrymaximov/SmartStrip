from fastapi import APIRouter, Depends
from app.utils.verification import verify_basic_auth


router = APIRouter()

@router.get("/")
async def root(auth: bool = Depends(verify_basic_auth)):
    return {
        "message": "Hi"
    }