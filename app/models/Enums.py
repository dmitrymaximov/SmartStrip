from enum import Enum


class StripState(str, Enum):
    OFF = "S00"
    ON = "S01"


class StripMode(str, Enum):
    BREATH = "M01"
    RAINBOW = "M02"
    RUNNER = "M03"
    SOLID = "M04"
    FIRE = "M05"


class StripColor(str, Enum):
    RED = "C01"
    ORANGE = "C02"
    YELLOW = "C03"
    GREEN = "C04"
    AZURE = "C05"
    BLUE = "C06"
    WHITE = "C07"
    PURPLE = "C08"
    PINK = "C09"
    TURQUOISE = "C10"


class StripBrightness(int, Enum):
    DIMLY = 25
    MEDIUM = 50
    BRIGHT = 100
