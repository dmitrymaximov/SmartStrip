from datetime import datetime, timezone, timedelta

from app.pkg_smart_strip.models.User import User


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

    def init_test_user(self, user_id: str = "000000000"):
        access_token: str = "token_id"
        expires_at: datetime = datetime.now(timezone.utc) + timedelta(days=1000)

        user = User(user_id=user_id, access_token=access_token, expires_at=expires_at)
        self.add_user(user)


users_cache = UserRegistry()
