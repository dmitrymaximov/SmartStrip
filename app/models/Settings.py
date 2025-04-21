from pydantic import BaseModel, field_validator, model_validator

from app.models.Enums import StripBrightness, StripColor, StripMode


class Setting(BaseModel):
    color: StripColor | None = None
    mode: StripMode = StripMode.RAINBOW
    brightness: StripBrightness | int = 100

    @field_validator("brightness")
    @classmethod
    def validate_brightness(cls, v: int) -> int:
        return max(0, min(100, v))

    @model_validator(mode="after")
    def validate_all_fields(self) -> "Setting":
        if self.mode in [StripMode.SOLID_COLOR] and self.color is None:
            self.color = StripColor.WHITE

        if self.mode in [StripMode.RAINBOW]:
            self.color = None

        return self
