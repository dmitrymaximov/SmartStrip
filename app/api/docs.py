from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html

from app.utils.verification import verify_basic_auth


router = APIRouter()

@router.get("/docs", response_class=HTMLResponse)
async def get_docs(auth: bool = Depends(verify_basic_auth)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger"
    )