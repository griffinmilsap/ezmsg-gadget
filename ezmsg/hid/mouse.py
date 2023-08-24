from . import write as hid_write

# This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
_MAX_MOUSE = (2 ** 15) - 1

def send_mouse_event(
        mouse_path: str = '/dev/hidg1', 
        buttons: chr = 0x00, # Individual buttons (8x)
        relative_x: float = 0.0, # 0.0-1.0
        relative_y: float = 0.0, # 0.0-1.0
        vertical_wheel_delta: float = 0.0, # 0.0-1.0 
        horizontal_wheel_delta: float = 0.0, # 0.0-1.0
    ):

    x = int(relative_x * _MAX_MOUSE)
    y = int(relative_y * _MAX_MOUSE)

    buf = [0] * 7
    buf[0] = buttons
    buf[1] = x & 0xff
    buf[2] = (x >> 8) & 0xff
    buf[3] = y & 0xff
    buf[4] = (y >> 8) & 0xff
    buf[5] = vertical_wheel_delta & 0xff
    buf[6] = horizontal_wheel_delta & 0xff
    hid_write.write_to_hid_interface(mouse_path, buf)
