from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi import Header, Response, Request
from fastapi.security import  HTTPBasic, HTTPBasicCredentials, OAuth2AuthorizationCodeBearer
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi import Query

from typing import Dict, List, Any
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

import uvicorn
import secrets
import httpx

from app.models.Device import Device, Capability, DeviceInfo, init_device_registry
from app.models.User import User, init_user_cache
from app.models.Enums import StripColor, StripState, StripMode, StripCommand, StripTest
from app.config import load_config



YANDEX_USERINFO_URL = "https://login.yandex.ru/info"
YANDEX_USERINFO_JSON_URL = "https://login.yandex.ru/info?format=json"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"


app = FastAPI(redoc_url=None, debug=True, docs_url=None)
security = HTTPBasic()
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://maxsfamily.ru/oauth/authorize",
    tokenUrl="https://maxsfamily.ru/oauth/token"
)

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections = set()
users_cache = init_user_cache()
app_config = load_config()
devices_registry: Dict[str, Device] = init_device_registry()

def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, app_config.login)
    correct_password = secrets.compare_digest(credentials.password, app_config.password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key != app_config.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return True


async def verify_websocket(websocket: WebSocket):
    api_key = websocket.headers.get("X-API-Key")
    if api_key != app_config.api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False
    return True


async def check_token(authorization: str = Header(...)) -> User:
    token = authorization.removeprefix("Bearer ").strip()
    user = next((u for u in users_cache.values() if u.access_token == token), None)

    if user:
        if user.is_token_valid():
            return user

        refreshed = await user.refresh(app_config.client_id, app_config.client_secret)
        if refreshed:
            return user

        users_cache.pop(user.user_id, None)

    # Токена в кеше нет — проверяем через Яндекс
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            YANDEX_USERINFO_URL,
            headers={"Authorization": f"OAuth {token}"}
        )

        if resp.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        userinfo = resp.json()

    expires_in = int(userinfo.get("expires_in", 3600))
    new_user = User.from_token_response(
        token=token,
        expires_in=expires_in,
        userinfo=userinfo
    )

    users_cache[new_user.user_id] = new_user
    return new_user


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    if not await verify_websocket(websocket):
        return

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
async def send_command(client_id: str, command: str, api_key: str = Depends(verify_api_key)):
    await send_command_to_esp32(f"{client_id}:{command}")
    return {"status": "ok", "msg": f"sent command: {command}"}


@app.get("/")
async def root(auth: bool = Depends(verify_basic_auth)):
    return {"message": f"Hi"}


@app.get("/docs", response_class=HTMLResponse)
async def get_docs(auth: bool = Depends(verify_basic_auth)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Swagger Docs"
    )


@app.get("/color", tags=["get"])
async def color(auth: bool = Depends(verify_basic_auth)) -> StripColor:
    return device.color


@app.post("/color", tags=["post"])
async def set_color(new_color: StripColor, api_key: str = Depends(verify_api_key)):
    device.color = new_color
    await send_command_to_esp32(f"{StripCommand.COLOR}:{device.color}")
    return {"success": True, "msg": "color updated"}


@app.get("/brightness_max", tags=["get"])
async def brightness(auth: bool = Depends(verify_basic_auth)) -> int:
    return device.brightnessMax


@app.post("/brightness_max", tags=["post"])
async def set_brightness_max(new_brightness: int, api_key: str = Depends(verify_api_key)):
    device.brightnessMax = new_brightness
    await send_command_to_esp32(f"{StripCommand.BRIGHT_MAX}:{device.brightnessMax}")
    return {"success": True, "msg": "brightness updated"}


@app.get("/mode", tags=["get"])
async def mode(auth: bool = Depends(verify_basic_auth)) -> StripMode:
    return device.mode


@app.post("/mode", tags=["post"])
async def set_mode(new_mode: StripMode, api_key: str = Depends(verify_api_key)):
    device.mode = new_mode
    await send_command_to_esp32(f"{StripCommand.MODE}:{device.mode}")
    return {"success": True, "msg": "mode updated"}


@app.get("/state", tags=["get"])
async def state(auth: bool = Depends(verify_basic_auth)) -> StripState:
    return device.state


@app.post("/state", tags=["post"])
async def set_state(new_state: StripState, api_key: str = Depends(verify_api_key)):
    device.state = new_state
    await send_command_to_esp32(f"{StripCommand.STATE}:{device.state}")
    return {"success": True, "msg": "state updated"}


@app.get("/test", tags=["get"])
async def test(auth: bool = Depends(verify_basic_auth)) -> StripTest:
    return device.test


@app.post("/test", tags=["post"])
async def set_debug_led(new_state: StripTest, api_key: str = Depends(verify_api_key)):
    await send_command_to_esp32(f"{StripCommand.TEST}:{new_state}")
    return {"success": True, "msg": "debug message sent"}


@app.head("/smart-strip/v1.0")
async def health_check():
    return Response(status_code=status.HTTP_200_OK)


@app.post("/smart-strip/v1.0/user/unlink")
async def unlink_user(request: Request, user: User = Depends(check_token)):
    users_cache.pop(user.user_id, None)
    request_id = request.headers.get("X-Request-Id")
    return {
        "request_id": request_id
    }


@app.get("/smart-strip/v1.0/user/devices")
async def get_devices(request: Request, user: User = Depends(check_token)):
    request_id = request.headers.get("X-Request-Id")
    user_id = user.user_id
    all_devices = list(devices_registry.values())

    return {
        "request_id": request_id,
        "payload": {
            "user_id": user_id,
            "devices": all_devices
        }
    }
    #return JSONResponse(status_code=status.HTTP_200_OK, content=content)


# Модель запроса для удобства
class QueryRequest(BaseModel):
    devices: List[Dict[str, str]]  # каждый элемент: {"id": "<device_id>"}

@app.post("/smart-strip/v1.0/user/devices/query")
async def query_devices(request: Request, body: QueryRequest, user: User = Depends(check_token)):
    request_id = request.headers.get("X-Request-Id")

    response_devices = []
    for item in body.devices:
        device = devices_registry.get(item["id"])
        if not device:
            continue  # или можно вернуть ошибку 404 для этого device_id

        # Собираем список capabilities с текущим состоянием
        capabilities = []
        for cap in device.capabilities:
            # определяем instance и value
            if cap.type == "devices.capabilities.on_off":
                instance = "on"
            else:
                # для range и подобных — берём instance из parameters
                instance = cap.parameters["instance"]  # e.g. "brightness"

            value = device.state.get(instance)
            capabilities.append({
                "type": cap.type,
                "state": {
                    "instance": instance,
                    "value": value
                }
            })

        response_devices.append({
            "id": device.id,
            "capabilities": capabilities
        })

    content = {
        "request_id": request_id,
        "payload": {
            "devices": response_devices
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


class ActionCapabilityState(BaseModel):
    instance: str
    value: Any

class ActionCapability(BaseModel):
    type: str
    state: ActionCapabilityState

class ActionDevice(BaseModel):
    id: str
    capabilities: List[ActionCapability]

class ActionRequest(BaseModel):
    devices: List[ActionDevice]


@app.post("/smart-strip/v1.0/user/devices/action")
async def action_devices(request: Request, body: ActionRequest, user: User = Depends(check_token)):
    request_id = request.headers.get("X-Request-Id")
    response_devices = []

    for action_dev in body.devices:
        # находим устройство в реестре
        dev = devices_registry.get(action_dev.id)
        if not dev:
            continue

        caps_result = []
        for cap in action_dev.capabilities:
            inst = cap.state.instance
            val = cap.state.value

            # изменяем локальное состояние устройства
            dev.state[inst] = val

            # формируем результат для этого capability
            caps_result.append({
                "type": cap.type,
                "state": {
                    "instance": inst,
                    "action_result": {
                        "status": "DONE"
                    }
                }
            })

        response_devices.append({
            "id": dev.id,
            "capabilities": caps_result
        })

    content = {
        "request_id": request_id,
        "payload": {
            "devices": response_devices
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Yandex"),
    state: str | None = Query(None, description="Optional state"),
):
    """
    Получаем code из запроса, обмениваем его на access_token + refresh_token,
    создаём User и сохраняем его в users_cache.
    В конце — редиректим пользователя на какую-нибудь страницу (или отдаем HTML).
    """
    # 1) Обмениваем code на токены
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": app_config.client_id,
        "client_secret": app_config.client_secret,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(YANDEX_TOKEN_URL, data=data)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token exchange failed: {resp.text}"
        )
    token_data = resp.json()
    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 3600)
    refresh_token = token_data.get("refresh_token")

    # 2) Получаем информацию о пользователе
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            "https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"}
        )
    if userinfo_resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch userinfo: {userinfo_resp.text}"
        )
    userinfo = userinfo_resp.json()

    # 3) Создаём экземпляр User и сохраняем в кэш
    user = User(
        user_id=userinfo["id"],
        display_name=userinfo.get("display_name"),
        email=userinfo.get("default_email"),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    )
    users_cache[user.user_id] = user

    # 4) Редирект (или можно вернуть JSON/HTML)
    # Предположим, у тебя есть фронтенд на http://localhost:3000/success
    redirect_url = f"https://your.frontend.domain/success?user_id={user.user_id}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)



if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=443,
                reload=True,
                ssl_keyfile="./ssl/key.pem",
                ssl_certfile="./ssl/cert.pem")
