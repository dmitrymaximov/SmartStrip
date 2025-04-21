from pydantic import BaseModel, validator


class Setting(BaseModel):
    brightness: int = 100

    @validator("brightness")
    def validate_brightness(cls, v):
        return max(0, min(100, v))


# Теперь будет работать:
s = Setting(brightness=-11)
print(s.brightness)
