from pydantic import BaseModel, Field

from app.models.Enums import StripColor, StripMode, StripState, StripTest


class Device(BaseModel):
    id: str = "smart-strip-1"
    name: str = "Умная лента"
    state: StripState = StripState.ON
    color: StripColor = StripColor.RED
    mode: StripMode = StripMode.RAINBOW
    test: StripTest = StripTest.OFF
    brightnessMax: int = Field(default=255, ge=0, le=255)

    