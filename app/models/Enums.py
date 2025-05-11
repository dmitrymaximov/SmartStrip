from enum import Enum


class StripCommand(str, Enum):
    STATE = "STATE"
    MODE = "MODE"
    COLOR = "COLOR"
    BRIGHTNESS = "BRIGHTNESS"


class StripState(str, Enum):
    OFF = "OFF"
    ON = "ON"


class StripMode(str, Enum):
    RAINBOW = "one"
    BREATH = "two"
    RUNNER = "three"
    FIRE = "four"
    SOLID = "five"
