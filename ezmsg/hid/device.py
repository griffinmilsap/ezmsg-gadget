import multiprocessing
import typing
import logging

from dataclasses import dataclass
import ezmsg.core as ez


class Error(Exception):
    pass


class WriteError(Error):
    pass


@dataclass
class ProcessResult:
    return_value: typing.Any = None
    exception: Exception = None

    def was_successful(self) -> bool:
        return self.exception is None


class ProcessWithResult(multiprocessing.Process):
    """A multiprocessing.Process object that keeps track of the child process'
    result (i.e., the return value and exception raised).

    Inspired by:
    https://stackoverflow.com/a/33599967/3769045
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the Connection objects used for communication between the
        # parent and child processes.
        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self):
        """Method to be run in sub-process."""
        result = ProcessResult()
        try:
            if self._target:
                result.return_value = self._target(*self._args, **self._kwargs)
        except Exception as e:
            result.exception = e
            raise
        finally:
            self.child_conn.send(result)

    def result(self):
        """Get the result from the child process.

        Returns:
            If the child process has completed, a ProcessResult object.
            Otherwise, a None object.
        """
        return self.parent_conn.recv() if self.parent_conn.poll() else None


def _write_to_hid_interface_immediately(hid_path, buffer):
    try:
        with open(hid_path, 'ab+') as hid_handle:
            hid_handle.write(buffer)
    except BlockingIOError:
        ez.logger.error(
            'Failed to write to HID interface: %s. Is USB cable connected?',
            hid_path)


def write_to_hid_interface(hid_path, buffer):
    # Avoid an unnecessary string formatting call in a write that requires low
    # latency.
    if ez.logger.getEffectiveLevel() == logging.DEBUG:
        ez.logger.debug_sensitive('writing to HID interface %s: %s', hid_path,
                               ' '.join([f'{x:#04x}' for x in buffer]))
    # Writes can hang, for example, when TinyPilot is attempting to write to the
    # mouse interface, but the target system has no GUI. To avoid locking up the
    # main server process, perform the HID interface I/O in a separate process.
    write_process = ProcessWithResult(
        target=_write_to_hid_interface_immediately,
        args=(hid_path, buffer),
        daemon=True)
    write_process.start()
    write_process.join(timeout=0.5)
    if write_process.is_alive():
        write_process.kill()
        _wait_for_process_exit(write_process)
    result = write_process.result()
    # If the result is None, it means the write failed to complete in time.
    if result is None or not result.was_successful():
        raise WriteError(f'Failed to write to HID interface: {hid_path}. '
                         'Is USB cable connected?')


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for _ in range(max_attempts):
        target_process.join(timeout=0.1)


from .messages import ReportMessage

from pathlib import Path
from aiofile import async_open, BinaryFileWrapper

from caio import linux_aio, thread_aio

class HIDDeviceSettings(ez.Settings):
    device: Path

class HIDDeviceState(ez.State):
    handle: BinaryFileWrapper

class HIDDevice(ez.Unit):

    SETTINGS: HIDDeviceSettings
    STATE: HIDDeviceState

    INPUT_HID = ez.InputStream(ReportMessage)

    async def initialize(self) -> None:
        linux_ctx = linux_aio.Context()
        threads_ctx = thread_aio.Context()
        self.STATE.handle = await async_open(
            self.SETTINGS.device, 'rb+', 
            context = threads_ctx
        )

    @ez.subscriber(INPUT_HID)
    async def write(self, msg: ReportMessage) -> None:
        await self.STATE.handle.write(msg.report())

    async def shutdown(self) -> None:
        await self.STATE.handle.close()
        