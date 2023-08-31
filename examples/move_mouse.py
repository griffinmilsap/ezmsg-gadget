import asyncio
import typing
import math
import time

from pathlib import Path

import ezmsg.core as ez

from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings
from ezmsg.gadget.messages import MouseMessage

class MouseMessageGeneratorSettings(ez.Settings):
    pub_rate: float = 10 # Hz

class MouseMessageGenerator(ez.Unit):
    SETTINGS: MouseMessageGeneratorSettings

    OUTPUT = ez.OutputStream(MouseMessage)

    @ez.publisher(OUTPUT)
    async def output_mouse(self) -> typing.AsyncGenerator:
        while True:
            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)

            w = 2.0 * math.pi * time.time()
            cpx = math.exp(w * 1.0j) * (math.cos(0.1 * w) + 1.0) / 2.0
            yield self.OUTPUT, MouseMessage(
                relative_x = (cpx.real / 2.0) + 1.0,
                relative_y = (cpx.imag / 2.0) + 1.0
            )

if __name__ == '__main__':

    generator = MouseMessageGenerator()

    mouse_device = HIDDevice(
        HIDDeviceSettings(
            device = Path('/dev/hidg1')
        )
    )

    ez.run(
        GENERATOR = generator,
        MOUSE_DEVICE = mouse_device,
        connections = (
            (generator.OUTPUT, mouse_device.INPUT_HID),
        )
    )



