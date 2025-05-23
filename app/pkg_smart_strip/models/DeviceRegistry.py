from fastapi import WebSocketDisconnect

from app.general.utils.logger import logger
from app.pkg_smart_strip.models.Device import SmartStripDevice


class DeviceRegistry:
    devices: list[SmartStripDevice] = list()

    def add_device(self, device: SmartStripDevice):
        self.devices.append(device)

    def get_device_by_id(self, device_id: str) -> SmartStripDevice | None:
        return next((device for device in self.devices if device.id == device_id), None)

    def get_devices(self) -> list[str]:
        return [device.id for device in self.devices]

    def remove_device(self, device):
        if device in self.devices:
            self.devices.remove(device)

    def remove_device_by_id(self, device_id: str):
        device = self.get_device_by_id(device_id)

        if device:
            self.devices.remove(device)

    def init_test_device(self, device_id="test"):
        device = SmartStripDevice(device_id)
        self.add_device(device)

    async def update_device_state(self, device: str | SmartStripDevice):
        device = self.get_device_by_id(device) if isinstance(device, str) else device

        if device:
            request = device.state.model_dump_json()
            logger.debug(request)

            try:
                await device.connection.send_text(request)
            except WebSocketDisconnect:
                self.remove_device(device)


devices_registry = DeviceRegistry()
