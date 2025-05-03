from dataclasses import dataclass
from pathlib import Path

from environs import Env


@dataclass
class Config:
    login: str
    password: str
    api_key: str


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(Path(__file__).parent.parent / ".env")

    return Config(
        login=env("LOGIN"),
        password=env("PASSWORD"),
        api_key=env("API_KEY")
    )


config = load_config()
