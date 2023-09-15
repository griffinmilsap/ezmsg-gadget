import typing

import ezmsg.core as ez

from ezmsg.gadget.function import Keyboard
from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings

class SendInterrupt(ez.Unit):
    OUTPUT = ez.OutputStream(Keyboard.Message)

    @ez.publisher(OUTPUT)
    async def interrupt(self) -> typing.AsyncGenerator:
        yield self.OUTPUT, Keyboard.Message(
            control_keys = Keyboard.MODIFIER_LEFT_CTRL, 
            hid_keycode = Keyboard.KEYCODE_C
        )

if __name__ == '__main__':

    generator = SendInterrupt()
    keyboard_device = HIDDevice(
        HIDDeviceSettings(
            function_name = 'keyboard0'
        )
    )

    ez.run(
        GENERATOR = generator,
        KEYBOARD_DEVICE = keyboard_device,
        connections = (
            (generator.OUTPUT, keyboard_device.INPUT_HID),
        )
    )
    