from dataclasses import dataclass

from usb_gadget import HIDFunction
from usb_gadget.usb_gadget import USBGadget

from ..hiddevice import HIDMessage

# This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
# FIXME: Maybe couple these definitions together
_MAX_MOUSE = (2 ** 15) - 1

class Mouse(HIDFunction):
    
    def __init__(self, gadget: USBGadget, name: str, **kwargs):
        super().__init__(gadget, name)

        self.protocol = '0'
        self.subclass = '0'
        self.report_length = '6'
        self.report_desc = bytes([
            0x05, 0x01,         # USAGE_PAGE (Generic Desktop)
            0x09, 0x02,         # USAGE (Mouse)
            0xA1, 0x01,         # COLLECTION (Application)

                                #   8-buttons
            0x05, 0x09,         #   USAGE_PAGE (Button)
            0x19, 0x01,         #   USAGE_MINIMUM (Button 1)
            0x29, 0x03,         #   USAGE_MAXIMUM (Button 3)
            0x15, 0x00,         #   LOGICAL_MINIMUM (0)
            0x25, 0x01,         #   LOGICAL_MAXIMUM (1)
            0x95, 0x03,         #   REPORT_COUNT (3)
            0x75, 0x01,         #   REPORT_SIZE (1)
            0x81, 0x02,         #   INPUT (Data,Var,Abs)
                                #   padding
            0x95, 0x01,         #   REPORT_COUNT (1)
            0x75, 0x05,         #   REPORT_SIZE (5)
            0x81, 0x03,         #   INPUT (Constant)

                                #   x, y, relative 16 bit
            0x05, 0x01,         #   USAGE_PAGE (Generic Desktop)
            0x09, 0x01,         #   USAGE (Pointer)
            0xA1, 0x00,         #   COLLECTION (Physical)
            0x09, 0x30,         #     USAGE (X)
            0x09, 0x31,         #     USAGE (Y)
            0x16, 0x01, 0x80,   #     LOGICAL_MINIMUM (-32767)
            0x26, 0xFF, 0x7F,   #     LOGICAL_MAXIMUM (32767)
            0x75, 0x10,         #     REPORT_SIZE (16),
            0x95, 0x02,         #     REPORT_COUNT (2),
            0x81, 0x06,         #     INPUT (Data,Var,Abs)
            0xC0,               #   END_COLLECTION

                                #   wheel, relative 8 bit
            0x09, 0x38,         #   USAGE (Wheel)
            0x15, 0x81,         #   LOGICAL_MINIMUM (-127)
            0x25, 0x7F,         #   LOGICAL_MAXIMUM (127)
            0x75, 0x08,         #   REPORT_SIZE (8),
            0x95, 0x01,         #   REPORT_COUNT (1),
            0x81, 0x06,         #   INPUT (Data,Var,Rel)

            0xC0                # END_COLLECTION
        ])

    @dataclass
    class Message(HIDMessage):
        buttons: int = 0x00 # Individual buttons (3x) [bit0 = LEFT, bit1 = RIGHT, bit2 = MIDDLE]
        relative_x: float = 0.0 # [-1.0-1.0]
        relative_y: float = 0.0 # [-1.0-1.0]
        relative_wheel: int = 0 # [0.0-1.0] 

        def report(self) -> bytearray:
            x = int(self.relative_x * _MAX_MOUSE)
            y = int(self.relative_y * _MAX_MOUSE)

            buf = [0] * 6
            buf[0] = self.buttons
            buf[1] = x & 0xff
            buf[2] = (x >> 8) & 0xff
            buf[3] = y & 0xff
            buf[4] = (y >> 8) & 0xff
            buf[5] = self.relative_wheel & 0xff

            return bytearray(buf)