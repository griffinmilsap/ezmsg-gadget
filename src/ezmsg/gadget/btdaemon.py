import os
import socket
import asyncio
import typing

from pathlib import Path
from importlib.resources import files

from dbus_next.aio.message_bus import MessageBus
from dbus_next.constants import BusType
from dbus_next.signature import Variant

from .config import GadgetConfig
from .function.hiddefinition import HIDDefinition



# Bluetooth HID L2CAP ports
# - defined by bluetooth HID standards
# - SDP configuration is universally ignored by clients.
P_CTRL = 0x0011 # Control port
P_INTR = 0x0013 # Interrupt port

# UUID for HID service (1124)
# https://www.bluetooth.com/specifications/assigned-numbers/service-discovery
HID_UUID = "00001124-0000-1000-8000-00805f9b34fb"


class BTHIDServer:

    loop: asyncio.AbstractEventLoop
    hid_clients: typing.Dict[asyncio.Task, asyncio.Queue[bytes]]
    tcp_server: asyncio.Task
    config: GadgetConfig
    report_map: typing.Dict[str, int]

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self.hid_clients = {}
        self.report_map = {}

    @classmethod
    async def start(cls, config_path: typing.Optional[Path] = None, loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> "BTHIDServer":

        config = GadgetConfig(config_path)

        if loop is None:
            loop = asyncio.get_running_loop()

        hid_server = cls(loop = loop)
        host, port = config.bluetooth_tcp_addr
        server = await asyncio.start_server(hid_server.handle_tcp_client, host = host, port = port)
        hid_server.tcp_server = loop.create_task(server.serve_forever(), name = 'bthid_tcp_server')
        hid_server.config = config
        return hid_server

    async def handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while True:
                data = await reader.readline()
                if not data: break
                for queue in self.hid_clients.values():
                    queue.put_nowait(data[:-1]) # Discard "newline"
        finally:
            writer.close()
    
    async def serve_forever(self) -> None:

        bus = await MessageBus(
            bus_type = BusType.SYSTEM,
            negotiate_unix_fd = True,
        ).connect()

        data_files = files('ezmsg.gadget')

        service_record = data_files.joinpath('sdp.xml').read_text()

        reports = ''
        report_id = 1
        for fn_name, (fn_class, _) in self.config.functions.items():
            if issubclass(fn_class, HIDDefinition):
                self.report_map[fn_name] = report_id
                reports += f'<sequence><uint8 value="0x22" /><text encoding="hex" value="{fn_class.REPORT_DESC.hex()}" /></sequence>'
                report_id += 1

        service_record.replace('[REPORTS]', reports)

        opts = {
            "Role": Variant('s', "server"),
            "RequireAuthentication": Variant('b', False),
            "RequireAuthorization": Variant('b', False),
            "AutoConnect": Variant('b', True),
            "ServiceRecord": Variant('s', service_record),
        }

        introspection = await bus.introspect("org.bluez", "/org/bluez")
        bluez = bus.get_proxy_object("org.bluez", "/org/bluez", introspection)

        manager = bluez.get_interface("org.bluez.ProfileManager1")

        await manager.call_register_profile("/bluez/ezmsg/gadget" , self.config.bluetooth_hid_uuid, opts) # type: ignore

        introspection = await bus.introspect("org.bluez", "/org/bluez/hci0")
        hci0 = bus.get_proxy_object("org.bluez", "/org/bluez/hci0", introspection)
        adapter_property = hci0.get_interface("org.freedesktop.DBus.Properties")

        address = await adapter_property.call_get("org.bluez.Adapter1", "Address") # type: ignore

        assert os.geteuid() == 0, "This won't work without root"

        async def handle_control_port(conn: socket.socket, _: typing.Tuple[str, int]) -> None:
            """ Not sure what the control port is for; we just keep it alive for now """
            try:
                while True:
                    data = await self.loop.sock_recv(conn, 1024)
                    if not data: break
            finally:
                conn.close()

        async def handle_interrupt_port(conn: socket.socket, info: typing.Tuple[str, int]) -> None:
            queue: asyncio.Queue[bytes] = asyncio.Queue()
            client_task = self.loop.create_task(self.handle_hid_client(conn, queue, info))
            client_task.add_done_callback(self.hid_clients.pop)
            self.hid_clients[client_task] = queue

        await asyncio.gather(
            serve_l2cap_socket(handle_control_port, address.value, P_CTRL, loop = self.loop),
            serve_l2cap_socket(handle_interrupt_port, address.value, P_INTR, loop = self.loop)
        )

    async def handle_hid_client(self, 
        interrupt: socket.socket, 
        queue: asyncio.Queue[bytes],
        info: typing.Tuple[str, int]
    ) -> None:
        print(f'Bluetooth client connected: {info=}')
        try:
            while True:
                packet = await queue.get()
                await self.loop.sock_sendall(interrupt, packet)
        except ConnectionResetError:
            pass
        finally:
            print(f'Bluetooth client disonnected: {info=}')
            interrupt.close()

ConnectionCallbackType = typing.Callable[[socket.socket,typing.Tuple[str, int]], typing.Coroutine[None, None, None],]

async def serve_l2cap_socket(
    callback: ConnectionCallbackType, 
    address: str, 
    port: int, 
    loop: typing.Optional[asyncio.AbstractEventLoop] = None
) -> None:

    if loop is None:
        loop = asyncio.get_running_loop()

    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP) # type: ignore
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((address, port))
    sock.listen(1)
    sock.setblocking(False)

    all_connection_tasks = set()
    while True:
        conn, info = await loop.sock_accept(sock)
        task = loop.create_task(callback(conn, info))
        task.add_done_callback(all_connection_tasks.remove)
        all_connection_tasks.add(task)


from .function import Keyboard, Mouse, Touch

async def test(device: str = 'keyboard0', keycode: int = 30, period: float = 1.0) -> None:
    config = GadgetConfig()
    reader, writer = await asyncio.open_connection(*(config.bluetooth_tcp_addr))

    try:
        while True:
            await asyncio.sleep(period)    
            writer.write(bytes([0xA1, 1]) + Keyboard.Message(0, keycode, tap = False).report() + bytes([ord('\n')]))
            await writer.drain()
            await asyncio.sleep(0.05)
            writer.write(bytes([0xA1, 1]) + Keyboard.Message(0, 0, tap = False).report() + bytes([ord('\n')]))
            await writer.drain()
    finally:
        writer.close()


async def main() -> None:
    server = await BTHIDServer.start()

    await asyncio.gather(
        server.serve_forever(),
        test(keycode = 30, period = 1.0),
        test(keycode = 31, period = 1.5)
    )

if __name__ == "__main__":

    asyncio.run(main())