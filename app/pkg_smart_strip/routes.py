from fastapi import APIRouter

from app.pkg_smart_strip.api.commands import router as esp_router
from app.pkg_smart_strip.api.devices import router as devices_router
from app.pkg_smart_strip.api.root import router as health_router
from app.pkg_smart_strip.api.user_devices import router as device_router
from app.pkg_smart_strip.api.user_devices_action import router as device_action_router
from app.pkg_smart_strip.api.user_devices_query import router as device_query_router
from app.pkg_smart_strip.api.user_unlink import router as unlink_router
from app.pkg_smart_strip.api.users import router as users_router
from app.pkg_smart_strip.api.websocket import router as websocket_router

router = APIRouter()

router.include_router(device_query_router)
router.include_router(device_router)
router.include_router(device_action_router)
router.include_router(health_router)
router.include_router(unlink_router)
router.include_router(esp_router)
router.include_router(devices_router)
router.include_router(users_router)
router.include_router(websocket_router)
