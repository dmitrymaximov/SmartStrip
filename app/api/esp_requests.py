from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends

from app.utils.verification import verify_basic_auth, verify_websocket, verify_api_key
from app.models.Device import Device, devices_registry
from app.models.Enums import StripColor, StripState, StripMode, StripCommand


router = APIRouter()
active_connections = set()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    if not await verify_websocket(websocket):
        return

    await websocket.accept()

    active_connections.add(websocket)
    print(f"New connection added with client_id = {client_id}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message from {client_id}: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Client {client_id} disconnected")


async def send_command_to_esp32(command: str):
    for connection in active_connections.copy():
        try:
            await connection.send_text(command)
        except WebSocketDisconnect:
            active_connections.remove(connection)


@router.post("/send-command/{client_id}")
async def send_command(command: str, api_key: str = Depends(verify_api_key)):
    await send_command_to_esp32(f"{command}")
    return {"status": "ok", "msg": f"sent command: {command}"}


@router.get("/color", tags=["esp"])
async def color(auth: bool = Depends(verify_basic_auth)) -> StripColor:
    pass


@router.post("/color", tags=["esp"])
async def set_color(new_color: StripColor, api_key: str = Depends(verify_api_key)):
    device.color = new_color
    await send_command_to_esp32(f"{StripCommand.COLOR}:{device.color}")
    return {"success": True, "msg": "color updated"}


@router.get("/brightness_max", tags=["esp"])
async def brightness(auth: bool = Depends(verify_basic_auth)) -> int:
    pass


@router.post("/brightness_max", tags=["esp"])
async def set_brightness_max(new_brightness: int, api_key: str = Depends(verify_api_key)):
    device.brightnessMax = new_brightness
    await send_command_to_esp32(f"{StripCommand.BRIGHT_MAX}:{device.brightnessMax}")
    return {"success": True, "msg": "brightness updated"}


@router.get("/mode", tags=["esp"])
async def mode(auth: bool = Depends(verify_basic_auth)) -> StripMode:
    pass


@router.post("/mode", tags=["esp"])
async def set_mode(new_mode: StripMode, api_key: str = Depends(verify_api_key)):
    device.mode = new_mode
    await send_command_to_esp32(f"{StripCommand.MODE}:{device.mode}")
    return {"success": True, "msg": "mode updated"}


@router.get("/state", tags=["esp"])
async def state(auth: bool = Depends(verify_basic_auth)) -> StripState:
    device = devices_registry["smart_strip"]
    state = StripState.ON if device.get_state() == True else StripState.OFF
    return state


@router.post("/state", tags=["esp"])
async def set_state(new_state: StripState, api_key: str = Depends(verify_api_key)):
    device = devices_registry["smart_strip"]
    await update_state(new_state=new_state, device=device)

    return {"success": True, "msg": "state updated"}


async def update_state(new_state: bool | StripState, device: Device):
    command = StripCommand.STATE
    value = None

    if isinstance(new_state, bool):
        value = StripState.ON if new_state == True else StripState.OFF
    elif isinstance(new_state, StripState):
        value = new_state

    await send_command_to_esp32(f"{command}:{value}")
    device.update_state(new_state)

    print("device state updated")



async def update_brightness():
    pass


async def update_mode():
    pass