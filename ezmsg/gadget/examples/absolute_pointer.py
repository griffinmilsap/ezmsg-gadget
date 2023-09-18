import asyncio
import typing
import math
import time

import numpy as np
import ezmsg.core as ez

from ezmsg.gadget.hiddevice import HIDDevice, HIDDeviceSettings
from ezmsg.gadget.function import Touch

class TouchMessageGeneratorSettings(ez.Settings):
    pub_rate: float = 60 # Hz

class TouchMessageGenerator(ez.Unit):
    SETTINGS: TouchMessageGeneratorSettings

    OUTPUT = ez.OutputStream(Touch.Message)

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
            yield self.OUTPUT, Touch.Message(
                touch = 0x02,
                absolute_x = (cpx.real + 1.0) / 2.0,
                absolute_y = (cpx.imag + 1.0) / 2.0
            )

if __name__ == '__main__':

    generator = TouchMessageGenerator()

    touch_device = HIDDevice(
        HIDDeviceSettings(
            function_name = 'touch0'
        )
    )

    ez.run(
        GENERATOR = generator,
        MOUSE_DEVICE = touch_device,
        connections = (
            (generator.OUTPUT, touch_device.INPUT_HID),
        )
    )



