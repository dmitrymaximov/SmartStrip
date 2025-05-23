from fastapi import APIRouter

from app.general.api.docs import router as docs_router
from app.general.api.root import router as root_router


router = APIRouter()

router.include_router(root_router)
router.include_router(docs_router)
