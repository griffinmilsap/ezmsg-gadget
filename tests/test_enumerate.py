import os
import tempfile

from pathlib import Path

import pytest

from ezmsg.gadget.config import setup_gadget, _GADGET_PATH

def test_enumerate():

    with tempfile.TemporaryDirectory() as fp:
        root = Path(fp)

        # Set up the relevant parts of this test filesystem
        gadget_path = root / _GADGET_PATH
        gadget_path.mkdir(parents = True, exist_ok = False)

        gadget = setup_gadget(root = root)

        gadget.activate('usb0')

        # ls /sys/class/udc > "${USB_DEVICE_PATH}/UDC"
        # chmod 777 /dev/hidg0
        # chmod 777 /dev/hidg1
        # systemctl restart dnsmasq.service

        gadget.deactivate()
        # gadget.destroy()

if __name__ == '__main__':
    test_enumerate()