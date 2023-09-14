import os
import typing
import importlib

from functools import reduce
from configparser import ConfigParser

from pathlib import Path

from usb_gadget import USBGadget, USBFunction

_CONFIG_ENV = 'EZMSG_GADGET_CONFIG'
_CONFIG_PATH = Path(os.environ.get(_CONFIG_ENV, '/etc/ezmsg-gadget.conf'))
_GADGET_PATH = Path('/sys/kernel/config/usb_gadget')
_EN_US = '0x409'

def _import_type(typestr: str) -> typing.Type[USBFunction]:
    module, name = typestr.split(":")
    module = importlib.import_module(module)
    ty = reduce(lambda t, n: getattr(t, n), [module] + name.split("."))

    if not isinstance(ty, type):
        raise ImportError(f"{typestr} does not resolve to type")

    return ty

def setup_gadget(
        config_path: typing.Optional[Path] = None, 
        setup_functions: bool = True,
        gadget_path: Path = _GADGET_PATH
    ) -> typing.Tuple[USBGadget, typing.Dict[str, USBFunction]]:

    if not gadget_path.exists():
        raise ValueError("Filesystem does not contain usb_gadget configfs")
    
    # Parse Config
    cfg = load_config(config_path)
    device_name = cfg.get('device', 'name', fallback = 'g1')
    # TODO: A lot more of this info could be brought in from the config file

    # Create gadget and set IDs
    gadget = USBGadget(device_name, path = str(gadget_path))
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

    functions: typing.Dict[str, USBFunction] = {}

    if setup_functions:
        for section in cfg.sections():
            tokens = section.split('.')
            if tokens[0] == 'function':
                name = tokens[-1]
                function_classname = tokens[-2]
                module = '.'.join(['ezmsg', 'gadget'] + tokens[:-2])
                ty = _import_type(f'{module}:{function_classname}')
                function = ty(gadget, name, **cfg[section])
                gadget.link(function, config)
                functions[name] = function

    return gadget, functions

def load_config(config_path: typing.Optional[Path] = None) -> ConfigParser:

    if config_path is None:
        config_path = Path('/') / _CONFIG_PATH

    config_files = []
    if config_path.exists() and config_path.is_file():
        config_files.append(config_path)
    config_dir = config_path.with_suffix('.d')
    if config_dir.exists() and config_dir.is_dir():
        for fname in config_dir.glob('*'):
            config_files.append(fname)

    config = ConfigParser()
    config.read(config_files)

    return config