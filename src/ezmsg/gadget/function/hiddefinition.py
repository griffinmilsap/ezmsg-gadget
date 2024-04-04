from usb_gadget import HIDFunction
from usb_gadget.usb_gadget import USBGadget

class HIDDefinition(HIDFunction):

    PROTOCOL: int
    SUBCLASS: int
    REPORT_LENGTH: int
    REPORT_DESC: bytes

    def __init__(self, gadget: USBGadget, name: str, **kwargs):
        super().__init__(gadget, name)
        self.protocol = str(self.__class__.PROTOCOL)
        self.subclass = str(self.__class__.SUBCLASS)
        self.report_length = str(self.__class__.REPORT_LENGTH)
        self.report_desc = self.__class__.REPORT_DESC