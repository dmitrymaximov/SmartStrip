from fastapi import APIRouter, Response, status


router = APIRouter()

@router.head("/smart-strip/v1.0", tags=["alisa"])
async def health_check():
    return Response(status_code=status.HTTP_200_OK)