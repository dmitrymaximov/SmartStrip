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


# Проверка базовой аутентификации
def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    correct_username = secrets.compare_digest(credentials.username, app_config.login)
    correct_password = secrets.compare_digest(credentials.password, app_config.password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


# Проверка API ключа
async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")) -> bool:
    if not api_key or api_key != app_config.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return True


# Проверка WebSocket соединения
async def verify_websocket(websocket: WebSocket) -> bool:
    api_key = websocket.headers.get("X-API-Key")
    if api_key != app_config.api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False
    return True


# Проверка токена через заголовок
async def verify_token(authorization: str = Header(...)) -> User:
    token = authorization.removeprefix("Bearer ").strip()

    # Ищем пользователя в кеше
    user = users_cache.get_user_by_token(token)

    if user:
        if user.is_token_valid():
            return user

        refreshed = await user.refresh(app_config.client_id, app_config.client_secret)
        if refreshed:
            return user

        # Если токен не валиден, удаляем пользователя из кеша
        users_cache.remove_user(user)

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

    users_cache.add_user(new_user)
    return new_user
