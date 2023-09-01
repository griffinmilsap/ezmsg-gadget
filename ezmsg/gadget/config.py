import typing

from pathlib import Path

from usb_gadget import USBGadget, USBFunction
from ezmsg.core.util import either_dict_or_kwargs

_GADGET_PATH = Path('sys/kernel/config/usb_gadget')
_EN_US = '0x409'

def setup_gadget(
    functions: typing.Optional[typing.Mapping[str, typing.Type[USBFunction]]] = None, 
    root: Path = Path('/'), 
    device_name: str = 'g1',
    **functions_kwargs: typing.Type[USBFunction],
) -> USBGadget:
    
    gadget_path = root / _GADGET_PATH

    if not gadget_path.exists():
        raise ValueError("Filesystem does not contain usb_gadget configfs")
    
    functions = either_dict_or_kwargs(functions, functions_kwargs, "setup_gadget")
    
    gadget = USBGadget(device_name, path = str(gadget_path))

    # Gadget ID
    gadget.idVendor  = '0x1d6b' # Linux Foundation
    gadget.idProduct = '0x0104' # Multifunction Composite Gadget
    gadget.bcdDevice = '0x0100' # V1.0.0
    gadget.bcdUSB    = '0x0200' # USB2

    # Gadget strings
    strings = gadget['strings'][_EN_US]
    strings.serialnumber = "657a6d736768696421"
    strings.manufacturer = 'ezmsg'
    strings.product = 'Multifunction ezmsg-gadget'

    # Create a config for the gadget
    config = gadget['configs']['c.1']
    config.bmAttributes = '0x80'
    config.MaxPower = '250'
    config['strings'][_EN_US].configuration = 'Config 1: ECM network'

    # Add functions
    for function_name, function in functions.items():
        fn = function(gadget, function_name)
        gadget.link(fn, config)

    return gadget

    

# ls /sys/class/udc > "${USB_DEVICE_PATH}/UDC"
# chmod 777 /dev/hidg0
# chmod 777 /dev/hidg1
# systemctl restart dnsmasq.service