import ezmsg.core as ez

from pathlib import Path
from aiofile import async_open, BinaryFileWrapper

from .messages import HIDMessage

class HIDDeviceSettings(ez.Settings):
    device: Path

class HIDDeviceState(ez.State):
    handle: BinaryFileWrapper

class HIDDevice(ez.Unit):

    SETTINGS: HIDDeviceSettings
    STATE: HIDDeviceState

    INPUT_HID = ez.InputStream(HIDMessage)

    async def initialize(self) -> None:
        self.STATE.handle = await async_open(self.SETTINGS.device, 'rb+')

    @ez.subscriber(INPUT_HID)
    async def write(self, msg: HIDMessage) -> None:
        await self.STATE.handle.write(msg.report())
        
