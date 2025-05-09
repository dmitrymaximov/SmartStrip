from enum import Enum


class StripCommand(str, Enum):
    TEST = "TEST"
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
    MUSIC = "six"


class StripColor(str, Enum):
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    AZURE = "AZURE"
    BLUE = "BLUE"
    WHITE = "WHITE"
    PURPLE = "PURPLE"
    PINK = "PINK"
    TURQUOISE = "TURQUOISE"


class StripTest(str, Enum):
    OFF = "OFF"
    ON = "ON"
