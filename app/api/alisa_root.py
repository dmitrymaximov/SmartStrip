from fastapi import APIRouter


router = APIRouter()

@router.head("/smart-strip/v1.0", tags=["alisa"])
async def health_check():
    return
