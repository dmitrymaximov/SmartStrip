from pydantic import BaseModel, Field

from app.models.Enums import StripColor, StripMode, StripState, StripTest


class Setting(BaseModel):
    state: StripState = StripState.ON
    color: StripColor = StripColor.RED
    mode: StripMode = StripMode.RAINBOW
    test: StripTest = StripTest.OFF
    brightness: int = Field(default=100, ge=0, le=255)
    brightnessMax: int = Field(default=255, ge=0, le=255)

    