from enum import Enum


class StripCommand(str, Enum):
    TEST = "TEST"
    STATE = "STATE"
    MODE = "MODE"
    COLOR = "COLOR"
    BRIGHT = "BRIGHT"
    BRIGHT_MAX = "BRIGHT_MAX"


class StripState(str, Enum):
    OFF = "OFF"
    ON = "ON"


class StripMode(str, Enum):
    BREATH = "BREATH"
    RAINBOW = "RAINBOW"
    RUNNER = "RUNNER"
    SOLID = "SOLID"
    FIRE = "FIRE"
    MUSIC = "MUSIC"


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
