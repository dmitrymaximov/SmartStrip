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


class UserRegistry:
    users: list[User] = list()

    def add_user(self, user: User):
        self.users.append(user)

    def get_user_by_id(self, user_id: str) -> User | None:
        return next((user for user in self.users if user.user_id == user_id), None)

    def get_user_by_token(self, token: str) -> User | None:
        return next((user for user in self.users if user.access_token == token), None)

    def get_users(self) -> list[str]:
        return [user.user_id for user in self.users]

    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)

    def remove_user_by_id(self, user_id: str):
        user = self.get_user_by_id(user_id)

        if user:
            self.users.remove(user)

    def init_test_user(self, user_id: str ="000000000"):
        access_token: str = "token_id"
        expires_at : datetime = datetime.now(timezone.utc) + timedelta(days=1000)

        user = User(user_id=user_id, access_token=access_token, expires_at=expires_at)
        self.add_user(user)


users_cache = UserRegistry()
users_cache.init_test_user()
