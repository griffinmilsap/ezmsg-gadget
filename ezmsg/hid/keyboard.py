from dataclasses import dataclass

from . import write as hid_write

import ezmsg.core as ez

@dataclass
class KeyboardMessage:
    control_keys: chr = 0x00
    hid_keycode: chr = 0x00

    def report(self) -> bytearray:
        buf = [0] * 8
        buf[0] = self.control_keys
        buf[2] = self.hid_keycode
        return bytearray(buf)
    
class KeyboardDeviceSettings(ez.Settings):
    keyboard_path: str = '/dev/hidg0'

class KeyboardDevice(ez.Unit):
    SETTINGS: KeyboardDeviceSettings
    INPUT = ez.InputStream(KeyboardMessage)

    @ez.subscriber(INPUT)
    async def on_msg(self, msg: KeyboardMessage) -> None:
        hid_write.write_to_hid_interface(
            self.SETTINGS.keyboard_path, 
            msg.report()
        )

        # If it's a normal keycode (i.e. not a standalone modifier key), add a
        # message indicating that the key should be released after it is sent. We do
        # this to prevent the keystroke from incorrectly repeating on the target
        # machine if network latency causes a delay between the keydown and keyup
        # events. However, auto-releasing has the disadvantage of preventing
        # genuinely long key presses (see
        # https://github.com/tiny-pilot/tinypilot/issues/1093).
        if msg.hid_keycode:
            hid_write.write_to_hid_interface(
                self.SETTINGS.keyboard_path, 
                KeyboardMessage().report()
            )
