from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from app.general.utils.logger import logger
from app.general.utils.verification import verify_websocket
from app.pkg_smart_strip.models.Device import SmartStripDevice
from app.pkg_smart_strip.models.DeviceRegistry import devices_registry

router = APIRouter()


@router.websocket("/smart-strip/v1.0/websocket/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    if not await verify_websocket(websocket):
        return

    await websocket.accept()

    new_device = SmartStripDevice(device_id=device_id, connection=websocket)
    devices_registry.add_device(new_device)

    logger.debug(f"New connection added with device_id = {device_id}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Message from {device_id}: {data}")
    except WebSocketDisconnect:
        devices_registry.remove_device_by_id(device_id)
        logger.debug(f"Client {device_id} disconnected")
