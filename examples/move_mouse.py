import asyncio
import typing
import math
import time

import numpy as np
import ezmsg.core as ez

from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings
from ezmsg.gadget.function import Mouse

class MouseMessageGeneratorSettings(ez.Settings):
    pub_rate: float = 10 # Hz

class MouseMessageGenerator(ez.Unit):
    SETTINGS: MouseMessageGeneratorSettings

    OUTPUT = ez.OutputStream(Mouse.Message)

    @ez.publisher(OUTPUT)
    async def output_mouse(self) -> typing.AsyncGenerator:
        start = time.time()
        while True:

            if time.time() - start > 2.0:
                raise ez.NormalTermination

            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)

            w = 2.0 * math.pi * 2.0 * time.time()
            mag = (np.cos(0.5 * w) + 1.0) / 2.0
            cpx = np.exp(w * 1.0j) * mag
            yield self.OUTPUT, Mouse.Message(
                relative_x = (cpx.real + 1.0) / 2.0,
                relative_y = (cpx.imag + 1.0) / 2.0
            )

if __name__ == '__main__':

    generator = MouseMessageGenerator()

    mouse_device = HIDDevice(
        HIDDeviceSettings(
            function_name = 'mouse0'
        )
    )

    ez.run(
        GENERATOR = generator,
        MOUSE_DEVICE = mouse_device,
        connections = (
            (generator.OUTPUT, mouse_device.INPUT_HID),
        )
    )



