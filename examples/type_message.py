import asyncio
import typing

import ezmsg.core as ez

from ezmsg.hid.keycodes import (
    MODIFIER_LEFT_SHIFT, 
    KEYCODE_NUMBER_1, 
    KEYCODE_A, 
    KEYCODE_FORWARD_SLASH
)

from ezmsg.hid.keyboard import KeyboardDevice, KeyboardMessage
#from ezmsg.util.debuglog import DebugLog

class GhostWriterSettings(ez.Settings):
    message: str
    pub_rate: float = 1 # Hz

class GhostWriter(ez.Unit):
    SETTINGS: GhostWriterSettings

    OUTPUT = ez.OutputStream(KeyboardMessage)

    @ez.publisher(OUTPUT)
    async def push_buttons(self) -> typing.AsyncGenerator:
        for character in self.SETTINGS.message:

            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)
            
            control_keys = 0x00
            keycode = 0x00

            if character.isdigit():
                keycode = ord(character) - ord('0') + KEYCODE_NUMBER_1
            elif character.isalpha():
                keycode = ord(character.lower()) - ord('a') + KEYCODE_A
                if character.isupper():
                    control_keys |= MODIFIER_LEFT_SHIFT
            else:
                # ?
                keycode = KEYCODE_FORWARD_SLASH
                control_keys |= MODIFIER_LEFT_SHIFT
            
            yield self.OUTPUT, KeyboardMessage(
                control_keys = control_keys, 
                hid_keycode = keycode
            )

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

    keyboard_device = KeyboardDevice()
    #log = DebugLog()

    ez.run(
        GENERATOR = generator,
        KEYBOARD_DEVICE = keyboard_device,
        #LOG = log,
        connections = (
            #(generator.OUTPUT, log.INPUT),
            (generator.OUTPUT, keyboard_device.INPUT),
        )
    )



