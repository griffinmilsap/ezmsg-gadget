import abc
import asyncio

from pathlib import Path

import ezmsg.core as ez

from aiofile import async_open, BinaryFileWrapper
from ezmsg.gadget.config import USBGadget, _GADGET_PATH


class HIDMessage(abc.ABC):
    @abc.abstractmethod
    def report(self) -> bytearray:
        raise NotImplementedError()


class HIDDeviceSettings(ez.Settings):
    function_name: str
    device_name: str = 'g1'
    root: Path = Path('/')


class HIDDeviceState(ez.State):
    handle: BinaryFileWrapper


class HIDDevice(ez.Unit):

    SETTINGS: HIDDeviceSettings
    STATE: HIDDeviceState

    INPUT_HID = ez.InputStream(HIDMessage)

    async def initialize(self) -> None:
        # Find the corresponding kernel object
        gadget_path = self.SETTINGS.root / _GADGET_PATH
        gadget = USBGadget(self.SETTINGS.device_name, path = str(gadget_path))
        kobj = gadget['functions'][f'hid.{self.SETTINGS.function_name}'].dev
        
        # Get the file descriptor that maps to that kernel object
        kobj_fd = self.SETTINGS.root / 'sys/dev/char' / str(kobj)
        command = f"udevadm info -r -q name {kobj_fd}"
        proc = await asyncio.create_subprocess_shell(command)
        stdout, stderr = await proc.communicate()
        descriptor = stdout.decode('ascii').strip()
        
        # Open the handle in binary mode read/append mode
        self.STATE.handle = await async_open(descriptor, 'rb+') # type: ignore

    @ez.subscriber(INPUT_HID)
    async def write(self, msg: HIDMessage) -> None:
        await self.STATE.handle.write(msg.report())
        