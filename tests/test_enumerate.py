import os
import tempfile

from pathlib import Path

import pytest

from ezmsg.gadget.config import setup_gadget, _GADGET_PATH
from ezmsg.gadget.mouse import MouseFunction
from ezmsg.gadget.keyboard import KeyboardFunction
from ezmsg.gadget.ethernet import EthernetFunction

def test_enumerate():

    with tempfile.TemporaryDirectory() as fp:
        root = Path(fp)

        # Set up the relevant parts of this test filesystem
        gadget_path = root / _GADGET_PATH
        gadget_path.mkdir(parents = True, exist_ok = False)

        gadget = setup_gadget(
            mouse_rel = MouseFunction, 
            keyboard0 = KeyboardFunction,
            usb0 = EthernetFunction,
            root = root
        )

        gadget.activate('usb0')
        gadget.deactivate()
        # gadget.destroy()

if __name__ == '__main__':
    test_enumerate()