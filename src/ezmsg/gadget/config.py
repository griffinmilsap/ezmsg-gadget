import os
import typing
import importlib

from functools import reduce
from configparser import ConfigParser

from pathlib import Path

from usb_gadget import USBGadget, USBFunction

CONFIG_ENV = 'EZMSG_GADGET_CONFIG'
CONFIG_PATH = Path(os.environ.get(CONFIG_ENV, '/etc/ezmsg-gadget.conf'))
GADGET_PATH = Path('/sys/kernel/config/usb_gadget')

_EN_US = '0x409'

def _import_type(typestr: str) -> typing.Type[USBFunction]:
    module, name = typestr.split(":")
    module = importlib.import_module(module)
    ty = reduce(lambda t, n: getattr(t, n), [module] + name.split("."))

    if not isinstance(ty, type):
        raise ImportError(f"{typestr} does not resolve to type")

    return ty

function_definition = typing.Dict[
    str, 
    typing.Tuple[
        typing.Type[USBFunction], 
        typing.Dict[str, str]
    ]
]

class GadgetConfig:

    parser: ConfigParser

    def __init__(self, config_path: typing.Optional[Path] = None):
        if config_path is None:
            config_path = Path('/') / CONFIG_PATH

        config_files = []
        if config_path.exists() and config_path.is_file():
            config_files.append(config_path)
        config_dir = config_path.with_suffix('.d')
        if config_dir.exists() and config_dir.is_dir():
            for fname in config_dir.glob('*'):
                config_files.append(fname)

        self.parser = ConfigParser()
        self.parser.read(config_files)

    @property
    def bluetooth_tcp_addr(self) -> typing.Tuple[str, int]:
        bt_host = self.parser.get('bluetooth', 'host', fallback = 'localhost')
        bt_port = int(self.parser.get('bluetooth', 'port', fallback = '6789'))
        return bt_host, bt_port
    
    @property
    def bluetooth_hid_uuid(self) -> str:
        return self.parser.get('bluetooth', 'uuid', fallback = "00001124-0000-1000-8000-00805f9b34fb")

    @property
    def gadget_name(self) -> str:
        return self.parser.get('gadget', 'name', fallback = 'g1')
    
    @property
    def endpoint_remote_addr(self) -> typing.Tuple[str, int]:
        remote_host = self.parser.get('endpoint', 'remote_host', fallback = 'localhost')
        remote_port = int(self.parser.get('endpoint', 'remote_port', fallback = '25978'))
        return remote_host, remote_port
    
    @property
    def functions(self) -> function_definition:
        functions: function_definition = {}

        for section in self.parser.sections():
            tokens = section.split('.')
            if tokens[0] == 'function':
                name = tokens[-1]
                function_classname = tokens[-2]
                module = '.'.join(['ezmsg', 'gadget'] + tokens[:-2])
                ty = _import_type(f'{module}:{function_classname}')
                functions[name] = (ty, dict(**self.parser[section]))

        return functions

def setup_gadget(
        config_path: typing.Optional[Path] = None, 
        setup_functions: bool = True,
        gadget_path: Path = GADGET_PATH
    ) -> typing.Tuple[USBGadget, typing.Dict[str, USBFunction]]:

    if not gadget_path.exists():
        raise ValueError("Filesystem does not contain usb_gadget configfs")
    
    cfg = GadgetConfig(config_path)

    # Create gadget and set IDs
    # TODO: A lot more of this info could be brought in from the config file
    gadget = USBGadget(cfg.gadget_name, path = str(gadget_path))
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
        for fn_name, (fn_type, kwargs) in cfg.functions.items():
            function = fn_type(gadget, fn_name, **kwargs)
            gadget.link(function, config)
            functions[fn_name] = function

    return gadget, functions