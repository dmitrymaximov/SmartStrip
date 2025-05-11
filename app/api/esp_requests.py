from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, status

from app.utils.verification import verify_basic_auth, verify_websocket, verify_api_key
from app.utils.logger import logger
from app.models.Device import Device, devices_registry
from app.models.Enums import StripState, StripMode, StripCommand

from typing import Any

router = APIRouter()
active_connections = set()

#todo need to refactor post methods

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    if not await verify_websocket(websocket):
        return

    await websocket.accept()

    active_connections.add(websocket)
    logger.debug(f"New connection added with client_id = {client_id}")

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Message from {client_id}: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.debug(f"Client {client_id} disconnected")


async def send_command_to_esp32(command: str):
    for connection in active_connections.copy():
        try:
            await connection.send_text(command)
        except WebSocketDisconnect:
            active_connections.remove(connection)


@router.post("/send-command")
async def send_command(command: str, api_key: str = Depends(verify_api_key)):
    await send_command_to_esp32(f"{command}")

    return {
        "status": "ok",
        "msg": f"sent command: {command}"
    }


@router.get("/color", tags=["esp"])
async def color(auth: bool = Depends(verify_basic_auth)):
    pass


@router.post("/color", tags=["esp"])
async def set_color(new_color: Any, api_key: str = Depends(verify_api_key)):
    device = devices_registry["smart_strip"]
    await update_color(new_color=new_color, device=device)

    return {
        "status": status.HTTP_200_OK,
        "msg": "color updated"
    }


@router.get("/brightness_max", tags=["esp"])
async def brightness(auth: bool = Depends(verify_basic_auth)) -> int:
    pass


@router.post("/brightness", tags=["esp"])
async def set_brightness(new_brightness: int, api_key: str = Depends(verify_api_key)):
    device = devices_registry["smart_strip"]
    await update_brightness(new_brightness=new_brightness, device=device)

    return {
        "status": status.HTTP_200_OK,
        "msg": "brightness updated"
    }


@router.get("/mode", tags=["esp"])
async def mode(auth: bool = Depends(verify_basic_auth)) -> StripMode:
    pass


@router.post("/mode", tags=["esp"])
async def set_mode(new_mode: StripMode, api_key: str = Depends(verify_api_key)):
    device = devices_registry["smart_strip"]
    await update_mode(new_mode=new_mode, device=device)

    return {
        "status": status.HTTP_200_OK,
        "msg": "mode updated"
    }


@router.get("/state", tags=["esp"])
async def state(auth: bool = Depends(verify_basic_auth)) -> StripState:
    device = devices_registry["smart_strip"]
    value = StripState.ON if device.get_state() == True else StripState.OFF
    return value


@router.post("/state", tags=["esp"])
async def set_state(new_state: StripState, api_key: str = Depends(verify_api_key)):
    device = devices_registry["smart_strip"]
    await update_state(new_state=new_state, device=device)

    return {
        "status": status.HTTP_200_OK,
        "msg": "state updated"
    }


async def update_state(new_state: bool | StripState, device: Device):
    command = StripCommand.STATE
    value = None

    if isinstance(new_state, bool):
        value = StripState.ON if new_state == True else StripState.OFF
    elif isinstance(new_state, StripState):
        value = new_state

    await send_command_to_esp32(f"{command}:{value}")
    device.update_state(new_state)

    logger.debug(f"device state updated to {value}")


async def update_brightness(new_brightness: int, device: Device):
    command = StripCommand.BRIGHTNESS
    value = max(0, min(100, new_brightness))

    await send_command_to_esp32(f"{command}:{value}")
    device.update_brightness(value)

    logger.debug(f"device brightness updated to {value}")


async def update_mode(new_mode: StripMode, device: Device):
    command = StripCommand.MODE
    value = new_mode

    await send_command_to_esp32(f"{command}:{value}")
    device.update_mode(value)

    logger.debug(f"device mode updated to {value}")


async def update_color(new_color: dict, device: Device):
    command = StripCommand.COLOR
    value = f"{new_color['h']},{new_color['s']},{new_color['v']}"

    await send_command_to_esp32(f"{command}:{value}")
    device.update_color(new_color)

    logger.debug(f"device color updated to {value}")
