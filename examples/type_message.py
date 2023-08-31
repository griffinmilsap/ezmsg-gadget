import asyncio
import typing

from pathlib import Path

import ezmsg.core as ez

from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings
from ezmsg.gadget.messages import KeyboardMessage
from ezmsg.gadget.keycodes import (
    MODIFIER_LEFT_SHIFT, 
    KEYCODE_NUMBER_1, 
    KEYCODE_A, 
    KEYCODE_FORWARD_SLASH,
    KEYCODE_ENTER
)

class GhostWriterSettings(ez.Settings):
    message: str
    pub_rate: float = 1 # Hz

class GhostWriter(ez.Unit):
    SETTINGS: GhostWriterSettings

    OUTPUT = ez.OutputStream(KeyboardMessage)

    @ez.publisher(OUTPUT)
    async def push_buttons(self) -> typing.AsyncGenerator:
        for character in self.SETTINGS.message:
            control_keys = 0x00
            keycode = 0x00

            if character.isdigit():
                keycode = ord(character) - ord('0') + KEYCODE_NUMBER_1
            elif character.isalpha():
                keycode = ord(character.lower()) - ord('a') + KEYCODE_A
                if character.isupper():
                    control_keys |= MODIFIER_LEFT_SHIFT
            else: # ?
                keycode = KEYCODE_FORWARD_SLASH
                control_keys |= MODIFIER_LEFT_SHIFT
            
            yield self.OUTPUT, KeyboardMessage(
                control_keys = control_keys, 
                hid_keycode = keycode
            )

            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)
        
        yield self.OUTPUT, KeyboardMessage(
            control_keys = 0x00,
            hid_keycode = KEYCODE_ENTER
        )

        await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)

        raise ez.Complete

if __name__ == '__main__':

    import argparse 

    parser = argparse.ArgumentParser(description = 'Keyboard typing demo')

    parser.add_argument(
        'message',
        type = str,
        help = 'message to type (keep it alphanumeric)'
    )

    class Args:
        message: str

    args = parser.parse_args(namespace = Args)

    generator = GhostWriter(
        GhostWriterSettings(
            message = args.message
        )
    )

    keyboard_device = HIDDevice(
        HIDDeviceSettings(
            Path('/dev/hidg0')
        )
    )

    ez.run(
        GENERATOR = generator,
        KEYBOARD_DEVICE = keyboard_device,
        connections = (
            (generator.OUTPUT, keyboard_device.INPUT_HID),
        )
    )



