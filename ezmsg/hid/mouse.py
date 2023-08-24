from dataclasses import dataclass

import ezmsg.core as ez

from . import write as hid_write

# This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
_MAX_MOUSE = (2 ** 15) - 1

@dataclass
class MouseMessage:
    buttons: chr = 0x00 # Individual buttons (8x)
    relative_x: float = 0.0 # 0.0-1.0
    relative_y: float = 0.0 # 0.0-1.0
    vertical_wheel_delta: chr = 0 # 0.0-1.0 
    horizontal_wheel_delta: chr = 0 # 0.0-1.0

    def report(self) -> bytearray:
        x = int(self.relative_x * _MAX_MOUSE)
        y = int(self.relative_y * _MAX_MOUSE)

        buf = [0] * 7
        buf[0] = self.buttons
        buf[1] = x & 0xff
        buf[2] = (x >> 8) & 0xff
        buf[3] = y & 0xff
        buf[4] = (y >> 8) & 0xff
        buf[5] = self.vertical_wheel_delta & 0xff
        buf[6] = self.horizontal_wheel_delta & 0xff

        return bytearray(buf)

class MouseDeviceSettings(ez.Settings):
    mouse_path: str = '/dev/hidg1'

class MouseDeviceState(ez.State):
    ...

class MouseDevice(ez.Unit):

    SETTINGS: MouseDeviceSettings
    STATE: MouseDeviceState

    INPUT = ez.InputStream(MouseMessage)

    @ez.subscriber(INPUT)
    async def on_mouse_msg(self, msg: MouseMessage) -> None:
        # TODO: Replace with aiofile; this blocks
        hid_write.write_to_hid_interface(self.SETTINGS.mouse_path, msg.report())

    
