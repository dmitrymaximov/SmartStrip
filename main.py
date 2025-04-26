from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import asyncio

from app.models.Settings import Setting
from app.models.Enums import StripColor, StripState, StripMode
from app.config import load_config


app = FastAPI()
app.debug = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections = set()
config = load_config()
setting = Setting()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections.add(websocket)
    print(f"New connection added: {websocket}")
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


@app.post("/send-command/{client_id}")
async def send_command(client_id: str, command: str):
    await send_command_to_esp32(f"{client_id}:{command}")
    return {"status": "command sent"}


@app.get("/")
async def root():
    return {"ok": True}


@app.get("/color", tags=["color"])
async def color() -> StripColor:
    return setting.color


@app.post("/color", tags=["color"])
async def set_color(new_color: StripColor):
    setting.color = new_color
    return {"success": True, "msg": "color updated"}


@app.get("/brightness", tags=["brightness"])
async def brightness() -> int:
    return setting.brightness


@app.post("/brightness", tags=["brightness"])
async def set_brightness(new_brightness: int):
    setting.brightness = new_brightness
    return {"success": True, "msg": "brightness updated"}


@app.get("/mode", tags=["mode"])
async def mode() -> StripMode:
    return setting.mode


@app.post("/mode", tags=["mode"])
async def set_mode(new_mode: StripMode):
    setting.mode = new_mode
    return {"success": True, "msg": "mode updated"}


@app.get("/state", tags=["state"])
async def state() -> StripState:
    return setting.state


@app.post("/state", tags=["state"])
async def set_state(new_state: StripState):
    setting.stat = new_state
    return {"success": True, "msg": "state updated"}


@app.get("/settings")
async def get_settings():
    return setting


@app.post("/settings")
async def set_settings(new_settings: Setting):
    global setting
    setting = new_settings
    return {"success": True, "msg": f"settings updated to {setting}"}


@app.post("/debug-led/{state}", tags=["debug"])
async def set_debug_led(new_state: bool):
    command = "led_on" if new_state else "led_off"
    await send_command_to_esp32(command)
    return {"success": True, "msg": "debug message sent"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
