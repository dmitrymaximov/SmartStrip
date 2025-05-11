from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from fastapi import status

import httpx


YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"


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
            raise ValueError("No refresh_token available")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(YANDEX_TOKEN_URL, data=data)
            if response.status_code == status.HTTP_200_OK:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data["expires_in"])
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                return True
            else:
                raise Exception(f"Error refreshing token: {response.text}")


def init_user_cache(test_user: bool = False) -> dict[str, User]:
    users: dict[str, User] = {}

    if test_user:
        user_id = "541998514"
        access_token = "y0__xCy-7iCAhiKwzcgsZmFghNtskQ8MzK1OYz-cOTd-ZrtOGiw9A"
        expires_at =  datetime.now(timezone.utc) + timedelta(seconds=10000)

        user = User(user_id=user_id, access_token=access_token, expires_at=expires_at)
        users[user.user_id] = user

    return users


users_cache = init_user_cache()
