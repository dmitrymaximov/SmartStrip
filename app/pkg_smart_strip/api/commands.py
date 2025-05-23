from fastapi import APIRouter, Depends

from app.general.utils.verification import verify_api_key
from app.pkg_smart_strip.models.Device import HSVColor, DeviceMode
from app.pkg_smart_strip.models.DeviceRegistry import devices_registry

router = APIRouter()


@router.get("/smart-strip/v1.0/color", tags=["smart_strip"])
async def color(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return {
            "h": device.state.hsv.h,
            "s": device.state.hsv.s,
            "v": device.state.hsv.v
        }
    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.post("/smart-strip/v1.0/color", tags=["smart_strip"])
async def set_color(device_id: str, new_color: HSVColor, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        device.state.hsv = new_color
        await devices_registry.update_device_state(device)
        return {"msg": f"Device state updated"}

    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.get("/smart-strip/v1.0/brightness", tags=["smart_strip"])
async def brightness(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return device.state.brightness

    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.post("/smart-strip/v1.0/brightness", tags=["smart_strip"])
async def set_brightness(device_id: str, new_brightness: int, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        device.state.brightness = new_brightness
        await devices_registry.update_device_state(device)
        return {"msg": f"Device state updated"}

    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.get("/smart-strip/v1.0/program", tags=["smart_strip"])
async def program(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return device.state.program

    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.post("/smart-strip/v1.0/program", tags=["smart_strip"])
async def set_program(device_id: str, new_program: DeviceMode, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        device.state.program = new_program
        await devices_registry.update_device_state(device)
        return {"msg": f"Device state updated"}

    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.get("/smart-strip/v1.0/state", tags=["smart_strip"])
async def state(device_id: str, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        return device.state.on

    return {"msg": f"Device with device_id = {device_id} unavailable"}


@router.post("/smart-strip/v1.0/state", tags=["smart_strip"])
async def set_state(device_id: str, new_state: bool, api_key: str = Depends(verify_api_key)):
    device = devices_registry.get_device_by_id(device_id)

    if device:
        device.state.on = new_state
        await devices_registry.update_device_state(device)
        return {"msg": f"Device state updated"}

    return {"msg": f"Device with device_id = {device_id} unavailable"}
