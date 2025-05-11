from dataclasses import dataclass
from pathlib import Path

from environs import Env


@dataclass
class Config:
    login: str
    password: str
    api_key: str
    client_id: str
    client_secret: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env_path = Path(path) if path else Path(__file__).parent.parent / ".env"
    env.read_env(env_path)

    return Config(
        login=env("LOGIN"),
        password=env("PASSWORD"),
        api_key=env("API_KEY"),
        client_id=env("CLIENT_ID"),
        client_secret=env("CLIENT_SECRET")
    )


app_config = load_config()
