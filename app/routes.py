from fastapi import APIRouter

from app.pkg_smart_strip.routes import router as smart_strip_router
from app.pkg_spreadsheet.routes import router as spreadsheet_router
from app.general.routes import router as common_router


router = APIRouter()

router.include_router(smart_strip_router)
router.include_router(spreadsheet_router)
router.include_router(common_router)
