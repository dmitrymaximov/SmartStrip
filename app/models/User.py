from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from fastapi import status

import httpx


class User(BaseModel):
    user_id: str
    display_name: str | None = None
    email: str | None = None
    access_token: str
    refresh_token: str | None = None
    expires_at: datetime


    @classmethod
    def from_token_response(cls, token: str, expires_in: int, userinfo: dict):
        return cls(
            user_id=userinfo["id"],
            access_token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        )


    def is_token_valid(self) -> bool:
        return datetime.now(timezone.utc) < self.expires_at


    async def refresh(self, client_id: str, client_secret: str) -> bool:
        if not self.refresh_token:
            print("Нет refresh_token, нельзя обновить токен")
            return False

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://oauth.yandex.ru/token", data=data)
            if response.status_code == status.HTTP_200_OK:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data["expires_in"])
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                print("Токен успешно обновлён")
                return True
            else:
                print("Ошибка при обновлении токена:", response.text)
                return False


def init_user_cache(with_test_user: bool = True):
    users_cache: dict[str, User] = {}

    user_id = "0"
    access_token = "8c0a8abb-b384-406b-b65c-5404de882b91"
    expires_at =  datetime.now(timezone.utc) + timedelta(seconds=10000)

    user = User(user_id=user_id, access_token=access_token, expires_at=expires_at)
    users_cache[user.user_id] = user

    return users_cache