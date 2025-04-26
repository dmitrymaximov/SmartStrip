from enum import Enum


class StripState(int, Enum):
    OFF = 0
    ON = 1


class StripMode(str, Enum):
    RAINBOW = "rainbow"
    SOLID_COLOR = "solid_color"


class StripColor(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    WHITE = "white"


class StripBrightness(int, Enum):
    DIMLY = 25
    MEDIUM = 50
    BRIGHT = 100
