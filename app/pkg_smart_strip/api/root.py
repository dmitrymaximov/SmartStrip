from fastapi import APIRouter

router = APIRouter()


@router.head("/smart-strip/v1.0", tags=["smart_strip"])
async def health_check():
    return
