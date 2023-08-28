from abc import abstractmethod, ABC
from dataclasses import dataclass

class ReportMessage(ABC):
    @abstractmethod
    def report(self) -> bytearray:
        raise NotImplementedError()

@dataclass
class KeyboardMessage(ReportMessage):
    control_keys: chr = 0x00
    hid_keycode: chr = 0x00
    tap: bool = True

    def report(self) -> bytearray:
        buf = [0] * 16
        buf[0] = self.control_keys
        buf[2] = self.hid_keycode
        return bytearray(buf[:(16 if self.tap else 8)])
    
# This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
_MAX_MOUSE = (2 ** 15) - 1

@dataclass
class MouseMessage(ReportMessage):
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