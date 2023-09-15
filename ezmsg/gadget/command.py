import argparse
import typing
import subprocess

from pathlib import Path

import ezmsg.core as ez

from usb_gadget import HIDFunction

from .config import GadgetConfig, setup_gadget
from .install import install, uninstall
from .hiddevice import HIDDevice, HIDDeviceSettings

def activate(config_path: typing.Optional[Path] = None) -> None:

    gadget, functions = setup_gadget(config_path = config_path)

    print('Activating Gadget')
    gadget.activate()

    # Change permissions of associated HID devices
    for fn_name, function in functions.items():
        if isinstance(function, HIDFunction):
            print(f'Changing permissions on {fn_name} -> {function.device}')
            subprocess.run(f'chmod 777 {function.device}', shell = True)


def deactivate(config_path: typing.Optional[Path] = None) -> None:

    gadget, _ = setup_gadget(config_path = config_path, setup_functions = False)

    print('Deactivating Gadget')
    gadget.deactivate()
    gadget.destroy()


def endpoint(config_path: typing.Optional[Path] = None) -> None:
    config = GadgetConfig(config_path)

    devices: typing.Dict[str, HIDDevice] = {}
    for function, (function_type, _) in config.functions.items():
        if issubclass(function_type, HIDFunction):
            devices[function] = HIDDevice(
                HIDDeviceSettings(
                    function_name = function, 
                )
            )
    
    ez.run(
        components = devices,
        graph_address = config.endpoint_remote_addr
    )

def cmdline() -> None:

    parser = argparse.ArgumentParser(
        description = "config and control"
    )

    parser.add_argument(
        'command',
        choices = ['activate', 'deactivate', 'install', 'uninstall', 'endpoint']
    )

    parser.add_argument(
        '--config', '-c',
        type = lambda x: Path(x),
        default = None,
        help = 'config file for gadget settings. default: /etc/ezmsg-gadget.conf'
    )

    ## UN/Install Flags
    parser.add_argument(
        '--install-endpoint-service',
        action = 'store_true',
        help = "install a service to launch 'ezmsg-gadget endpoint' on boot"
    )

    parser.add_argument(
        '--no-boot-service',
        action = 'store_true',
        help = "don't install a boot service for 'ezmsg-gadget activate'"
    )

    parser.add_argument(
        '--yes', '-y',
        action = 'store_true',
        help = 'yes to all questions for interactive install/uninstall'
    )

    class Args:
        command: str
        config: typing.Optional[Path]
        install_endpoint_service: bool
        no_boot_service: bool
        yes: bool

    args = parser.parse_args(namespace = Args)

    if args.command in ['activate', 'deactivate', 'install', 'uninstall']:
        try:
            if args.command == 'activate':
                activate(args.config)
            elif args.command == 'deactivate':
                deactivate(args.config)
            elif args.command == 'install':
                install(
                    boot_service = not args.no_boot_service,
                    endpoint_service = args.install_endpoint_service,
                    yes = args.yes
                )
            elif args.command == 'uninstall':
                uninstall(
                    yes = args.yes
                )

        except PermissionError:
            print('Permission Error. Run this as superuser.')  
            raise

    elif args.command == 'endpoint':
        endpoint(args.config)

if __name__ == '__main__':
    cmdline()