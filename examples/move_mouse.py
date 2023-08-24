import asyncio
import time
import typing
import math

import ezmsg.core as ez

from ezmsg.hid.mouse import MouseDevice, MouseMessage
from ezmsg.util.debuglog import DebugLog

class MouseMessageGeneratorSettings(ez.Settings):
    pub_rate: float = 50 # Hz

class MouseMessageGenerator(ez.Unit):
    SETTINGS: MouseMessageGeneratorSettings

    OUTPUT = ez.OutputStream(MouseMessage)

    @ez.publisher(OUTPUT)
    async def output_mouse(self) -> typing.AsyncGenerator:
        while True:
            await asyncio.sleep(1.0 / self.SETTINGS.pub_rate)

            now = time.time()
            yield self.OUTPUT, MouseMessage(
                relative_x = math.cos(now),
                relative_y = math.sin(now)
            )

if __name__ == '__main__':

    generator = MouseMessageGenerator()
    mouse_device = MouseDevice()
    # log = DebugLog()

    ez.run(
        GENERATOR = generator,
        MOUSE_DEVICE = mouse_device,
        # LOG = log,
        connections = (
            # (generator.OUTPUT, log.INPUT),
            (generator.OUTPUT, mouse_device.INPUT)
        )
    )



