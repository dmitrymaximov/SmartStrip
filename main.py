from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Header
from fastapi.security import  HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


import uvicorn
import secrets

from app.models.Settings import Setting
from app.models.Enums import StripColor, StripState, StripMode, StripCommand, StripTest
from app.config import load_config


app = FastAPI(redoc_url=None, debug=True, docs_url=None)
security = HTTPBasic()

app.add_middleware(HTTPSRedirectMiddleware)
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

def verify_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, config.login)
    correct_password = secrets.compare_digest(credentials.password, config.password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key != config.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return True


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
async def send_command(client_id: str, command: str, auth: bool = Depends(verify_api_key)):
    await send_command_to_esp32(f"{client_id}:{command}")
    return {"status": "ok", "msg": f"sent command: {command}"}


@app.get("/")
async def root(auth: bool = Depends(verify_auth)):
    return {"message": f"Hi"}


@app.get("/docs", response_class=HTMLResponse)
async def get_docs(auth: bool = Depends(verify_auth)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger Docs"
    )


@app.get("/color", tags=["get"])
async def color(auth: bool = Depends(verify_auth)) -> StripColor:
    return setting.color


@app.post("/color", tags=["post"])
async def set_color(new_color: StripColor, api_key: str = Depends(verify_api_key)):
    setting.color = new_color
    await send_command_to_esp32(f"{StripCommand.COLOR}:{setting.color}")
    return {"success": True, "msg": "color updated"}


@app.get("/brightness", tags=["get"])
async def brightness(auth: bool = Depends(verify_auth)) -> int:
    return setting.brightness


@app.post("/brightness", tags=["post"])
async def set_brightness(new_brightness: int):
    setting.brightness = new_brightness
    await send_command_to_esp32(f"{StripCommand.BRIGHT}:{setting.brightness}")
    return {"success": True, "msg": "brightness updated"}


@app.post("/brightness_max", tags=["post"])
async def set_brightness_max(new_brightness: int):
    setting.brightnessMax = new_brightness
    await send_command_to_esp32(f"{StripCommand.BRIGHT_MAX}:{setting.brightnessMax}")
    return {"success": True, "msg": "brightness updated"}


@app.get("/mode", tags=["get"])
async def mode(auth: bool = Depends(verify_auth)) -> StripMode:
    return setting.mode


@app.post("/mode", tags=["post"])
async def set_mode(new_mode: StripMode):
    setting.mode = new_mode
    await send_command_to_esp32(f"{StripCommand.MODE}:{setting.mode}")
    return {"success": True, "msg": "mode updated"}


@app.get("/state", tags=["get"])
async def state(auth: bool = Depends(verify_auth)) -> StripState:
    return setting.state


@app.post("/state", tags=["post"])
async def set_state(new_state: StripState):
    setting.state = new_state
    await send_command_to_esp32(f"{StripCommand.STATE}:{setting.state}")
    return {"success": True, "msg": "state updated"}


@app.get("/test", tags=["get"])
async def test(auth: bool = Depends(verify_auth)) -> StripTest:
    return setting.test


@app.post("/test/", tags=["post"])
async def set_debug_led(new_state: StripTest):
    await send_command_to_esp32(f"{StripCommand.TEST}:{new_state}")
    return {"success": True, "msg": "debug message sent"}



if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=443,
                reload=True,
                ssl_keyfile="./ssl/key.pem",
                ssl_certfile="./ssl/cert.pem")
