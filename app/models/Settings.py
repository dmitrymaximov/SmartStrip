from pydantic import BaseModel, model_validator, Field

from app.models.Enums import StripColor, StripMode, StripState


class Setting(BaseModel):
    state: StripState = StripState.OFF
    color: StripColor | None = StripColor.WHITE
    mode: StripMode = StripMode.RAINBOW
    brightness: int = Field(default=100, ge=0, le=255)
    brightnessMax: int = Field(default=255, ge=0, le=255)

    @model_validator(mode="after")
    def validate_all_fields(self) -> "Setting":
        if self.mode in [StripMode.SOLID] and self.color is None:
            self.color = StripColor.WHITE

        if self.mode in [StripMode.RAINBOW]:
            self.color = None

        if self.brightness < 0:
            self.brightness = 0

        if self.brightness > self.brightnessMax:
            self.brightness = self.brightnessMax - 1

        return self
