from fastapi import APIRouter

from app.api.devices import router as device_router
from app.api.devices_action import router as device_action_router
from app.api.devices_query import router as device_query_router
from app.api.alisa_root import router as health_router
from app.api.user_unlink import router as unlink_router
from app.api.esp_requests import router as esp_router
from app.api.docs import router as docs_router
from app.api.root import router as root_router


router = APIRouter()

router.include_router(device_query_router)
router.include_router(device_router)
router.include_router(device_action_router)
router.include_router(health_router)
router.include_router(unlink_router)
router.include_router(esp_router)
router.include_router(docs_router)
router.include_router(root_router)
