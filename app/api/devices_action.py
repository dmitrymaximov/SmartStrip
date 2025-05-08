from fastapi import APIRouter, Depends, Request

from pydantic import BaseModel
from typing import List, Dict, Any

from app.models.User import User
from app.models.Device import devices_registry
from app.utils.verification import verify_token
from app.api.esp_requests import update_state, update_brightness

router = APIRouter()

class ActionCapabilityState(BaseModel):
    instance: str
    value: Any


class ActionCapability(BaseModel):
    type: str
    state: ActionCapabilityState


class ActionDevice(BaseModel):
    id: str
    custom_data: Dict[str, Any] | None = None
    capabilities: List[ActionCapability]


class ActionPayload(BaseModel):
    devices: List[ActionDevice]


class ActionRequest(BaseModel):
    payload: ActionPayload



@router.post("/smart-strip/v1.0/user/devices/action", tags=["alisa"])
async def action_devices(request: Request, body: ActionRequest, user: User = Depends(verify_token)):
    request_id = request.headers.get("X-Request-Id")
    response_devices = []

    for action_dev in body.payload.devices:
        dev = devices_registry.get(action_dev.id)
        if not dev:
            continue

        caps_result = []

        for cap in action_dev.capabilities:
            inst = cap.state.instance
            val = cap.state.value

            print(f"Device {dev.id} action: {inst} = {val}")

            if inst == "on":
                if val not in [True, False]:
                    print(f"Invalid value for {inst} on device {dev.id}")
                    caps_result.append({
                        "type": cap.type,
                        "state": {
                            "instance": inst,
                            "action_result": {
                                "status": "ERROR",
                                "error_code": "INVALID_VALUE",
                                "error_message": f"Invalid value {val} for {inst}"
                            }
                        }
                    })
                    continue

                # изменяем локальное состояние устройства
                dev.state[inst] = val
                await update_state(new_state=val, device=dev)

                # формируем результат для этого capability
                caps_result.append({
                    "type": cap.type,
                    "state": {
                        "instance": inst,
                        "action_result": {
                            "status": "DONE"
                        }
                    }
                })
            elif inst == "brightness":
                if not isinstance(val, int) or not (0 <= val <= 100):
                    caps_result.append({
                        "type": cap.type,
                        "state": {
                            "instance": inst,
                            "action_result": {
                                "status": "ERROR",
                                "error_code": "INVALID_VALUE",
                                "error_message": f"Expected int 0-100 for {inst}, got {val}"
                            }
                        }
                    })
                    continue

                dev.state[inst] = val
                await update_brightness(new_brightness=val, device=dev)

                caps_result.append({
                    "type": cap.type,
                    "state": {
                        "instance": inst,
                        "action_result": {"status": "DONE"}
                    }
                })

            else:
                # handle other capabilities like brightness if applicable
                print(f"Unsupported capability instance: {inst} for device {dev.id}")
                caps_result.append({
                    "type": cap.type,
                    "state": {
                        "instance": inst,
                        "action_result": {
                            "status": "ERROR",
                            "error_code": "UNSUPPORTED_CAPABILITY",
                            "error_message": f"Unsupported capability {inst}"
                        }
                    }
                })

        response_devices.append({
            "id": dev.id,
            "capabilities": caps_result
        })

    return {
        "request_id": request_id,
        "payload": {
            "devices": response_devices
        }
    }
