from fastapi import APIRouter

from app.api.alisa.user_devices import router as device_router
from app.api.alisa.user_devices_action import router as device_action_router
from app.api.alisa.user_devices_query import router as device_query_router
from app.api.alisa.alisa_root import router as health_router
from app.api.alisa.user_unlink import router as unlink_router
from app.api.esp.esp_requests import router as esp_router
from app.api.general.docs import router as docs_router
from app.api.general.root import router as root_router
from app.api.general.devices import router as devices_router
from app.api.general.users import router as users_router


router = APIRouter()

router.include_router(device_query_router)
router.include_router(device_router)
router.include_router(device_action_router)
router.include_router(health_router)
router.include_router(unlink_router)
router.include_router(esp_router)
router.include_router(docs_router)
router.include_router(root_router)
router.include_router(devices_router)
router.include_router(users_router)
