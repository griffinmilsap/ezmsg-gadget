import typing

from pathlib import Path

import ezmsg.core as ez

from ezmsg.gadget.keycodes import MODIFIER_LEFT_CTRL, KEYCODE_C
from ezmsg.gadget.messages import KeyboardMessage
from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings

class SendInterrupt(ez.Unit):
    OUTPUT = ez.OutputStream(KeyboardMessage)

    @ez.publisher(OUTPUT)
    async def interrupt(self) -> typing.AsyncGenerator:
        yield self.OUTPUT, KeyboardMessage(
            control_keys = MODIFIER_LEFT_CTRL, 
            hid_keycode = KEYCODE_C
        )

if __name__ == '__main__':

    generator = SendInterrupt()
    keyboard_device = HIDDevice(
        HIDDeviceSettings(
            device = Path('/dev/hidg0')
        )
    )

    ez.run(
        GENERATOR = generator,
        KEYBOARD_DEVICE = keyboard_device,
        connections = (
            (generator.OUTPUT, keyboard_device.INPUT_HID),
        )
    )
    