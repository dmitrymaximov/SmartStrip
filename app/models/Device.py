from pydantic import BaseModel


class DeviceAction(BaseModel):
    id: str
    capabilities: list

class UnlinkRequest(BaseModel):
    request_id: str

class DevicesRequest(BaseModel):
    request_id: str
