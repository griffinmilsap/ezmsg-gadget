import os
import argparse
import typing
import configparser

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


def enumerate() -> None:
    # Arguments for mouse, keyboard, ethernet (and mac addresses)
    ...

def remove_all() -> None:
    # Remove all UDC functions and configs
    # Note enumerate is supposed to do this on shutdown but we provide this on 
    # commandline to clean up files in case enumerate fails for whatever reason
    ...

def serve() -> None:
    # Serve HID endpoints
    ...

def cmdline() -> None:

    parser = argparse.ArgumentParser(
        description = "configuration"
    )

    # Add a -y for yes

    args = parser.parse_args()

    # install, enumerate, remove_all require superuser permissions
    # Check for superuser HERE

    # serve doesn't require superuser