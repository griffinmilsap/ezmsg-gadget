
from usb_gadget import USBFunction
from usb_gadget.usb_gadget import USBGadget

class Ethernet(USBFunction):
    
    def __init__(
        self, 
        gadget: USBGadget, 
        name: str = 'usb0', 
        host_addr: str = "60:6D:3C:3E:0C:7B", 
        dev_addr: str = "60:6D:3C:3E:0C:6B",
        **kwargs
    ) -> None:
        super().__init__(gadget, 'ecm.' + name)

        self.host_addr = host_addr
        self.dev_addr = dev_addr
