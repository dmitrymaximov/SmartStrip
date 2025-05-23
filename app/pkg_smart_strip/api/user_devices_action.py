from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.general.utils.verification import verify_token
from app.pkg_smart_strip.models.DeviceRegistry import devices_registry
from app.pkg_smart_strip.models.User import User

router = APIRouter()


class ActionCapabilityState(BaseModel):
    instance: str
    value: Any


class ActionCapability(BaseModel):
    type: str
    state: ActionCapabilityState


class ActionDevice(BaseModel):
    id: str
    custom_data: dict[str, Any] | None = None
    capabilities: list[ActionCapability]


class ActionPayload(BaseModel):
    devices: list[ActionDevice]


class ActionRequest(BaseModel):
    payload: ActionPayload


@router.post("/smart-strip/v1.0/user/devices/action", tags=["smart_strip"])
async def action_devices(request: Request, body: ActionRequest, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")
    response_devices = []

    for requested_device in body.payload.devices:
        device_id = requested_device.id
        device = devices_registry.get_device_by_id(device_id)
        if not device:
            continue

        caps_result = []

        for cap in requested_device.capabilities:
            inst = cap.state.instance
            val = cap.state.value
            status = "ERROR"
            error_code = None
            error_message = None

            if inst == "on":
                if val in [True, False]:
                    device.state.on = val
                    await devices_registry.update_device_state(device)
                    status = "DONE"
                else:
                    error_code = "INVALID_VALUE"
                    error_message = f"Invalid value {val} for 'on'"

            elif inst == "brightness":
                if isinstance(val, int) and 0 <= val <= 100:
                    device.state.brightness = val
                    await devices_registry.update_device_state(device)
                    status = "DONE"
                else:
                    error_code = "INVALID_VALUE"
                    error_message = f"Invalid brightness value: {val}"

            elif inst == "program":
                if val in ["one", "two", "three", "four", "five"]:
                    device.state.program = val
                    await devices_registry.update_device_state(device)
                    status = "DONE"
                else:
                    error_code = "INVALID_VALUE"
                    error_message = f"Invalid mode: {val}"

            elif inst == "hsv":
                if isinstance(val, dict) and all(k in val for k in ["h", "s", "v"]):
                    device.state.hsv = val
                    await devices_registry.update_device_state(device)
                    status = "DONE"
                else:
                    error_code = "INVALID_VALUE"
                    error_message = f"Invalid HSV value: {val}"

            else:
                error_code = "UNSUPPORTED_CAPABILITY"
                error_message = f"Unsupported capability instance: {inst}"

            result = {
                "type": cap.type,
                "state": {
                    "instance": inst,
                    "action_result": {
                        "status": status
                    }
                }
            }

            if status == "ERROR":
                result["state"]["action_result"].update({
                    "error_code": error_code,
                    "error_message": error_message
                })

            caps_result.append(result)

        response_devices.append({
            "id": device.id,
            "capabilities": caps_result
        })

    return {
        "request_id": request_id,
        "payload": {
            "devices": response_devices
        }
    }
