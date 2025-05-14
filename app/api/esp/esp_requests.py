from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends

from app.utils.verification import verify_websocket, verify_api_key
from app.utils.logger import logger
from app.models.Device import Device, SmartStripDevice, devices_registry, HSVColor
from app.models.Enums import StripState, StripMode, StripCommand


router = APIRouter()


@router.websocket("/ws/{device_id}")
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


async def send_command_to_esp32(device: str | Device, command: str):
    device = devices_registry.get_device_by_id(device) if isinstance(device, str) else device

    try:
        await device.connection.send_text(command)
    except WebSocketDisconnect:
        devices_registry.remove_device(device)


@router.post("/send-command", tags=["esp post"])
async def send_command(device_id: str, command: str, api_key: str = Depends(verify_api_key)):
    await send_command_to_esp32(device_id, command)

    return {
        "status": "ok",
        "msg": f"sent command: {command} to device: {device_id}"
    }


@router.get("/color", tags=["esp get"])
async def color(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return {
            "h": device.state.hsv.h,
            "s": device.state.hsv.s,
            "v": device.state.hsv.v
        }
    return {
        "msg": f"device with id {device_id} isn't exist"
    }


@router.post("/color", tags=["esp post"])
async def set_color(device_id: str, new_color: HSVColor, api_key: str = Depends(verify_api_key)):
    await update_color(device_id=device_id, color=new_color)

    return {
        "msg": f"sent event to update color"
    }


@router.get("/brightness_max", tags=["esp get"])
async def brightness(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return {
            device.state.brightness
        }
    return {
        "msg": f"device with id {device_id} isn't exist"
    }


@router.post("/brightness", tags=["esp post"])
async def set_brightness(device_id: str, new_brightness: int, api_key: str = Depends(verify_api_key)):
    await update_brightness(device_id=device_id, brightness=new_brightness)

    return {
        "msg": f"sent event to update brightness"
    }


@router.get("/mode", tags=["esp get"])
async def mode(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return {
            device.state.program
        }
    return {
        "msg": f"device with id {device_id} isn't exist"
    }


@router.post("/mode", tags=["esp post"])
async def set_mode(device_id: str, new_mode: StripMode, api_key: str = Depends(verify_api_key)):
    await update_mode(device_id=device_id, mode=new_mode)

    return {
        "msg": f"sent event to update mode"
    }


@router.get("/state", tags=["esp get"])
async def state(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return {
            device.state.on
        }
    return {
        "msg": f"device with id {device_id} isn't exist"
    }


@router.post("/state", tags=["esp post"])
async def set_state(device_id: str, new_state: StripState, api_key: str = Depends(verify_api_key)):
    await update_state(device_id=device_id, state=new_state)

    return {
        "msg": f"sent event to update state"
    }


async def update_state(device_id: str, state: bool | StripState):
    value = None

    if isinstance(state, bool):
        value = StripState.ON if state == True else StripState.OFF
    elif isinstance(state, StripState):
        value = state

    command = f"{StripCommand.STATE}:{value}"

    device = devices_registry.get_device_by_id(device_id)

    if device:
        await send_command_to_esp32(device=device, command=command)
        device.state.program = state
        logger.debug(f"device state updated to {value}")
    else:
        logger.debug(f"device with id {device_id} isn't exist")


async def update_brightness(device_id: str, brightness: int):
    value = max(0, min(100, brightness))
    command = f"{StripCommand.BRIGHTNESS}:{value}"

    device = devices_registry.get_device_by_id(device_id)

    if device:
        await send_command_to_esp32(device=device, command=command)
        device.state.brightness = value
        logger.debug(f"device brightness updated to {value}")
    else:
        logger.debug(f"device with id {device_id} isn't exist")


async def update_mode(device_id: str, mode: StripMode):
    value = mode
    command = f"{StripCommand.MODE}:{value}"

    device = devices_registry.get_device_by_id(device_id)

    if device:
        await send_command_to_esp32(device=device, command=command)
        device.state.program = value
        logger.debug(f"device mode updated to {value}")
    else:
        logger.debug(f"device with id {device_id} isn't exist")


async def update_color(device_id: str, color: HSVColor):
    value = f"{color.h},{color.s},{color.v}"
    command = f"{StripCommand.COLOR}:{value}"

    device = devices_registry.get_device_by_id(device_id)

    if device:
        await send_command_to_esp32(device=device, command=command)
        device.state.hsv = color
        logger.debug(f"device color updated to {value}")
    else:
        logger.debug(f"device with id {device_id} isn't exist")

