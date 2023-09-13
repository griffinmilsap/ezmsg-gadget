from dataclasses import dataclass

from usb_gadget import HIDFunction
from usb_gadget.usb_gadget import USBGadget

from .hiddevice import HIDMessage

class MouseFunction(HIDFunction):
    
    def __init__(self, gadget: USBGadget, name: str):
        super().__init__(gadget, name)

        self.protocol = '0'
        self.subclass = '0'
        self.report_length = '7'
        self.report_desc = bytes([
            0x05, 0x01,         # USAGE_PAGE (Generic Desktop)
            0x09, 0x02,         # USAGE (Mouse)
            0xA1, 0x01,         # COLLECTION (Application)
                                #   8-buttons
            0x05, 0x09,         #   USAGE_PAGE (Button)
            0x19, 0x01,         #   USAGE_MINIMUM (Button 1)
            0x29, 0x08,         #   USAGE_MAXIMUM (Button 8)
            0x15, 0x00,         #   LOGICAL_MINIMUM (0)
            0x25, 0x01,         #   LOGICAL_MAXIMUM (1)
            0x95, 0x08,         #   REPORT_COUNT (8)
            0x75, 0x01,         #   REPORT_SIZE (1)
            0x81, 0x02,         #   INPUT (Data,Var,Abs)
                                #   x,y absolute coordinates
            0x05, 0x01,         #   USAGE_PAGE (Generic Desktop)
            0x09, 0x30,         #   USAGE (X)
            0x09, 0x31,         #   USAGE (Y)
            0x16, 0x00, 0x00,   #   LOGICAL_MINIMUM (0)
            0x26, 0xFF, 0x7F,   #   LOGICAL_MAXIMUM (32767)
            0x75, 0x10,         #   REPORT_SIZE (16)
            0x95, 0x02,         #   REPORT_COUNT (2)
            0x81, 0x02,         #   INPUT (Data,Var,Abs)
                                #   vertical wheel
            0x09, 0x38,         #   USAGE (wheel)
            0x15, 0x81,         #   LOGICAL_MINIMUM (-127)
            0x25, 0x7F,         #   LOGICAL_MAXIMUM (127)
            0x75, 0x08,         #   REPORT_SIZE (8)
            0x95, 0x01,         #   REPORT_COUNT (1)
            0x81, 0x06,         #   INPUT (Data,Var,Rel)
                                #   horizontal wheel
            0x05, 0x0C,         #   USAGE_PAGE (Consumer Devices)
            0x0A, 0x38, 0x02,   #   USAGE (AC Pan)
            0x15, 0x81,         #   LOGICAL_MINIMUM (-127)
            0x25, 0x7F,         #   LOGICAL_MAXIMUM (127)
            0x75, 0x08,         #   REPORT_SIZE (8)
            0x95, 0x01,         #   REPORT_COUNT (1)
            0x81, 0x06,         #   INPUT (Data,Var,Rel)
            0xC0,               # END_COLLECTION
        ])

# This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
# FIXME: Maybe couple these definitions together
_MAX_MOUSE = (2 ** 15) - 1

@dataclass
class MouseMessage(HIDMessage):
    buttons: int = 0x00 # Individual buttons (8x)
    relative_x: float = 0.0 # 0.0-1.0
    relative_y: float = 0.0 # 0.0-1.0
    vertical_wheel_delta: int = 0 # 0.0-1.0 
    horizontal_wheel_delta: int = 0 # 0.0-1.0

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