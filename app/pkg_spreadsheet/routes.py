from fastapi import APIRouter

from app.pkg_spreadsheet.api.add_new_expense import router as write_router
from app.pkg_spreadsheet.api.alice import router as alice_router


router = APIRouter()

router.include_router(write_router)
router.include_router(alice_router)
