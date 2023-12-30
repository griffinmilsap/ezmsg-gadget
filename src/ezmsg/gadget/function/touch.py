from dataclasses import dataclass

from usb_gadget import HIDFunction
from usb_gadget.usb_gadget import USBGadget

from ..hiddevice import HIDMessage

# This comes from LOGICAL_MAXIMUM in the touch HID descriptor.
# FIXME: Maybe couple these definitions together
_MAX_TOUCH = 10000

class Touch(HIDFunction):
    
    def __init__(self, gadget: USBGadget, name: str, **kwargs):
        super().__init__(gadget, name)

        self.protocol = '0'
        self.subclass = '0'
        self.report_length = '5'
        self.report_desc = bytes([
            0x05, 0x0d,                    # USAGE_PAGE (Digitizer)
            0x09, 0x02,                    # USAGE (Pen)
            0xa1, 0x01,                    # COLLECTION (Application)
            
            # declare a finger collection
            0x09, 0x20,                    #   Usage (Stylus)
            0xA1, 0x00,                    #   Collection (Physical)

            # Declare a finger touch (finger up/down)
            0x09, 0x42,                    #     Usage (Tip Switch)
            0x09, 0x32,                    #     USAGE (In Range)
            0x15, 0x00,                    #     LOGICAL_MINIMUM (0)
            0x25, 0x01,                    #     LOGICAL_MAXIMUM (1)
            0x75, 0x01,                    #     REPORT_SIZE (1)
            0x95, 0x02,                    #     REPORT_COUNT (2)
            0x81, 0x02,                    #     INPUT (Data,Var,Abs)

            # Declare the remaining 6 bits of the first data byte as constant -> the driver will ignore them
            0x75, 0x01,                    #     REPORT_SIZE (1)
            0x95, 0x06,                    #     REPORT_COUNT (6)
            0x81, 0x01,                    #     INPUT (Cnst,Ary,Abs)

            # Define absolute X and Y coordinates of 16 bit each (percent values multiplied with 100)
            # http:#www.usb.org/developers/hidpage/Hut1_12v2.pdf
            # Chapter 16.2 says: "In the Stylus collection a Pointer physical collection will contain the axes reported by the stylus."
            0x05, 0x01,                    #     Usage Page (Generic Desktop)
            0x09, 0x01,                    #     Usage (Pointer)
            0xA1, 0x00,                    #     Collection (Physical)
            0x09, 0x30,                    #        Usage (X)
            0x09, 0x31,                    #        Usage (Y)
            0x16, 0x00, 0x00,              #        Logical Minimum (0)
            0x26, 0x10, 0x27,              #        Logical Maximum (10000)
            0x36, 0x00, 0x00,              #        Physical Minimum (0)
            0x46, 0x10, 0x27,              #        Physical Maximum (10000)
            0x66, 0x00, 0x00,              #        UNIT (None)
            0x75, 0x10,                    #        Report Size (16),
            0x95, 0x02,                    #        Report Count (2),
            0x81, 0x02,                    #        Input (Data,Var,Abs)
            0xc0,                          #     END_COLLECTION

            0xc0,                          #   END_COLLECTION
            0xc0                           # END_COLLECTION
        ])

    @dataclass
    class Message(HIDMessage):
        touch: int = 0x00 # Individual buttons (3x) [bit0 = up/down, bit1 = in range]
        absolute_x: float = 0.0 # [0-1.0]
        absolute_y: float = 0.0 # [0-1.0]

        def report(self) -> bytearray:
            x = int(self.absolute_x * _MAX_TOUCH)
            y = int(self.absolute_y * _MAX_TOUCH)

            buf = [0] * 5
            buf[0] = self.touch
            buf[1] = x & 0xff
            buf[2] = (x >> 8) & 0xff
            buf[3] = y & 0xff
            buf[4] = (y >> 8) & 0xff

            return bytearray(buf)