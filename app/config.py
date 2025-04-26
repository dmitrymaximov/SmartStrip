from dataclasses import dataclass
from pathlib import Path

from environs import Env


@dataclass
class Config:
    max_brightness: int


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(Path(__file__).parent.parent / ".env")

    return Config(
        max_brightness=env("MAX_BRIGHTNESS")
    )


config = load_config()
