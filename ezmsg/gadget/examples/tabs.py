import asyncio
import typing

import ezmsg.core as ez

from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings
from ezmsg.gadget.function import Keyboard

class TabsSettings(ez.Settings):
    pub_rate: float = 1 # Hz

class Tabs(ez.Unit):
    SETTINGS: TabsSettings

    OUTPUT = ez.OutputStream(Keyboard.Message)

    @ez.publisher(OUTPUT)
    async def push_buttons(self) -> typing.AsyncGenerator:

        while True:

            yield self.OUTPUT, Keyboard.Message(
                control_keys = 0x00, 
                hid_keycode = Keyboard.KEYCODE_TAB
            )

            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)

if __name__ == '__main__':

    generator = Tabs()

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



