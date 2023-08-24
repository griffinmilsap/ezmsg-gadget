import typing

import ezmsg.core as ez

from ezmsg.hid.keycodes import MODIFIER_LEFT_CTRL, KEYCODE_C
from ezmsg.hid.keyboard import KeyboardDevice, KeyboardMessage

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
    keyboard_device = KeyboardDevice()

    ez.run(
        GENERATOR = generator,
        KEYBOARD_DEVICE = keyboard_device,
        connections = (
            (generator.OUTPUT, keyboard_device.INPUT),
        )
    )



