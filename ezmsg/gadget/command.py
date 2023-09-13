import os
import argparse
import typing
import time
import configparser

from .config import setup_gadget
from .keyboard import KeyboardFunction
from .mouse import MouseFunction
from .ethernet import EthernetFunction

from pathlib import Path

import ezmsg.core as ez

def _confirm_prompt(question: str, yes: bool = False) -> bool:
    reply = None if not yes else ""
    while reply not in ("", "y", "n"):
        reply = input(f"{question} (Y/n): ").lower()
    response = (reply in ("", "y"))
    if response:
        ez.logger.info(f'ACTION: {question}')
    return response

_MODULES_DIR = lambda root: root / 'etc' / 'modules-load.d'
_SERVICE_DIR = lambda root: root / 'lib' / 'systemd' / 'system'
_ENUMERATE_SERVICE_FILE = 'ezmsg-gadget-enumerate.service'

# TODO Set this up with configparser
def _ENUMERATE_SERVICE() -> str:
    return """
    [Unit]
    Description=Initialize ezmsg-gadget USB gadgets
    After=syslog.target

    [Service]
    Type=oneshot
    User=root
    ExecStart=/opt/gadget-priveliged/init-usb-gadget
    RemainAfterExit=true
    ExecStop=/opt/gadget-priveliged/remove-usb-gadget
    StandardOutput=journal

    [Install]
    WantedBy=local-fs.target
    """

_ENDPOINT_SERVICE_FILE = 'ezmsg-gadget-serve.service'
_ENDPOINT_SERVICE = """
[Unit]
Description=Initialize ezmsg-gadget USB gadgets
After=syslog.target

[Service]
Type=oneshot
User=root
ExecStart=/opt/gadget-priveliged/init-usb-gadget
RemainAfterExit=true
ExecStop=/opt/gadget-priveliged/remove-usb-gadget
StandardOutput=journal

[Install]
WantedBy=local-fs.target
"""


def install(root: Path = Path('/'), service: bool = True, yes: bool = False) -> None:
    # Add dwc, libcomposite to modules
    modules_dir = _MODULES_DIR(root)

    if _confirm_prompt(f'Add dwc2 to {modules_dir}', yes):
        with open(modules_dir / 'dwc2', 'w') as f:
            f.write('dwc2')

    if _confirm_prompt(f'Add libcomposite to {modules_dir}', yes):
        with open(modules_dir / 'libcomposite', 'w') as f:
            f.write('libcomposite')

    # Add a systemd startup file
    service_dir = _SERVICE_DIR(root)

    if service and _confirm_prompt(f'Add {_ENUMERATE_SERVICE_FILE} to {service_dir}', yes):
        with open(service_dir / _ENUMERATE_SERVICE_FILE, 'w') as f:
            f.write(_ENUMERATE_SERVICE())

        if _confirm_prompt(f'Enable {_ENUMERATE_SERVICE_FILE}', yes):
            # Enable Service
            ...

    ez.logger.info("ezmsg-gadget install completed.  reboot encouraged.")

def uninstall(root: Path = Path('/'), yes: bool = False) -> None:

    # Stop/disable services
    service_dir = _SERVICE_DIR(root)

    services: typing.List[Path] = [
        service_dir / _ENUMERATE_SERVICE_FILE,
        service_dir / _ENDPOINT_SERVICE_FILE,
    ]

    for service in services:
        if service.exists():
            if _confirm_prompt(f'Stop/Disable {service.name}', yes):
                # Disable service
                ...

    modules_dir = _MODULES_DIR(root)

    # Remove everything placed by install
    files = services + [
        modules_dir / 'dwc2',
        modules_dir / 'libcomposite',
    ]

    for f in files:
        if f.exists() and _confirm_prompt(f'Remove {f}', yes):
            os.remove(f)

    ez.logger.info("ezmsg-gadget uninstall completed.  reboot encouraged.")


def enumerate(config: Path) -> None:

    gadget = setup_gadget(
        mouse_rel = MouseFunction, 
        keyboard0 = KeyboardFunction,
        usb0 = EthernetFunction,
    )

    ez.logger.info('Activating Gadget')
    gadget.activate()

    # TODO: Ensure users can interact with hidg devices
    # Maybe this is best done by changing the group instead of chmod 777
    # chmod 777 /dev/hidg0
    # chmod 777 /dev/hidg1

    # TODO: Maybe restart dnsmasq?
    # systemctl restart dnsmasq.service

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        ez.logger.info('Interrupted')

    ez.logger.info('Deactivating Gadget')

    gadget.deactivate()
    gadget.destroy()

def serve() -> None:
    # Serve HID endpoints
    ...

def cmdline() -> None:

    parser = argparse.ArgumentParser(
        description = "config and control"
    )

    parser.add_argument(
        'command',
        choices = ['enumerate', 'install', 'uninstall']
    )

    parser.add_argument(
        '--config', '-c',
        type = lambda x: Path(x),
        default = Path('/etc/ezmsg-gadget.conf'),
        help = 'config file for gadget settings; only used with enumerate'
    )

    parser.add_argument(
        '--yes', '-y',
        action = 'store_true',
        help = 'yes to all questions for interactive install/uninstall'
    )

    class Args:
        command: str
        config: Path
        yes: bool

    args = parser.parse_args(namespace = Args)

    if args.command in ['enumerate', 'install', 'uninstall']:
        try:
            if args.command == 'enumerate':
                enumerate(args.config)
        except PermissionError:
            ez.logger.error('Permission Error. Run this as superuser.')  
            raise

    elif args.command == 'serve':
        ...