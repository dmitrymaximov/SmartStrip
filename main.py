from fastapi import FastAPI

from app.models.Settings import Setting


app = FastAPI()
app.debug = True

setting = Setting()
led_state = False


@app.post("/color")
async def set_color(color: str):
    pass


@app.post("/brightness")
async def set_brightness(brightness: int):
    pass


@app.post("/mode")
async def set_mode(mode: str):
    pass


@app.post("/settings")
async def set_settings(settings: Setting):
    payload = {"mode": settings.mode, "color": settings.color, "brightness": settings.brightness}
    global setting
    setting = Setting(**payload)
    return setting


@app.get("/settings")
async def get_settings():
    return setting


@app.get("/led")
async def get_led():
    return led_state
