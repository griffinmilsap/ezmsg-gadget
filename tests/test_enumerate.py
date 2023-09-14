import tempfile

from pathlib import Path

import pytest

from ezmsg.gadget.config import setup_gadget

def test_enumerate():

    with tempfile.TemporaryDirectory() as tempdir:
        gadget, _ = setup_gadget(gadget_path = Path(tempdir))
        gadget.activate('usb0')
        gadget.deactivate()

if __name__ == '__main__':
    test_enumerate()