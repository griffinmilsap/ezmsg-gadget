import asyncio
import typing

import ezmsg.core as ez

from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings
from ezmsg.gadget.function import Keyboard

class GhostWriterSettings(ez.Settings):
    message: str
    pub_rate: float = 3 # Hz

class GhostWriter(ez.Unit):
    SETTINGS: GhostWriterSettings

    OUTPUT = ez.OutputStream(Keyboard.Message)

    @ez.publisher(OUTPUT)
    async def push_buttons(self) -> typing.AsyncGenerator:
        for character in self.SETTINGS.message:
            control_keys = 0x00
            keycode = 0x00

            if character.isdigit():
                keycode = ord(character) - ord('0') + Keyboard.KEYCODE_NUMBER_1
            elif character.isalpha():
                keycode = ord(character.lower()) - ord('a') + Keyboard.KEYCODE_A
                if character.isupper():
                    control_keys |= Keyboard.MODIFIER_LEFT_SHIFT
            elif character == ' ':
                keycode = Keyboard.KEYCODE_SPACEBAR
            elif character == ',':
                keycode = Keyboard.KEYCODE_COMMA
            elif character == '.':
                keycode = Keyboard.KEYCODE_PERIOD
            else: # ?
                keycode = Keyboard.KEYCODE_FORWARD_SLASH
                control_keys |= Keyboard.MODIFIER_LEFT_SHIFT
            
            yield self.OUTPUT, Keyboard.Message(
                control_keys = control_keys, 
                hid_keycode = keycode
            )

            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)
        
        yield self.OUTPUT, Keyboard.Message(
            control_keys = 0x00,
            hid_keycode = Keyboard.KEYCODE_ENTER
        )

        await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)

        raise ez.Complete

if __name__ == '__main__':

    import argparse 

    parser = argparse.ArgumentParser(description = 'Keyboard typing demo')

    parser.add_argument(
        '--message', '-m',
        type = str,
        help = 'message to type (keep it alphanumeric)',
        default = 'Wake up, Neo...'
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



