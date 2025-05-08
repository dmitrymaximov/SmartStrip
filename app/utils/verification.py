from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi import Header, Response, Request
from fastapi.security import  HTTPBasic, HTTPBasicCredentials, OAuth2AuthorizationCodeBearer
import secrets
import httpx

from app.models.User import User, users_cache
from app.utils.config import app_config

AUTHORIZATION_URL = "https://maxsfamily.ru/oauth/authorize"
TOKEN_URL = "https://maxsfamily.ru/oauth/token"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"



security = HTTPBasic()
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTHORIZATION_URL,
    tokenUrl=TOKEN_URL
)

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


async def verify_token(authorization: str = Header(...)) -> User:
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