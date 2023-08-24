from dataclasses import dataclass

from . import write as hid_write

import ezmsg.core as ez

@dataclass
class KeyboardMessage:
    control_keys: chr = 0x00
    hid_keycode: chr = 0x00
    tap: bool = True

    def report(self) -> bytearray:
        buf = [0] * 16
        buf[0] = self.control_keys
        buf[2] = self.hid_keycode
        return bytearray(buf[:(16 if self.tap else 8)])
    
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
