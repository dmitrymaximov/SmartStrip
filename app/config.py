from dataclasses import dataclass


# from environs import Env


@dataclass
class Config:
    color: str | None = None
    mode: str = "rainbow"
    brightness: int = 100
    max_brightness: int = 100


"""
def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        color=env("COLOR"),
        mode=env("MODE"),
        brightness=env("BRIGHTNESS"),
        max_brightness=env("MAX_BRIGHTNESS")
    )


config = load_config('../.env')
"""
