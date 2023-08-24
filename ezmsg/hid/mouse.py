from . import write as hid_write

# This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
_MAX_MOUSE = (2 ** 15) - 1

def send_mouse_event(mouse_path, buttons, relative_x, relative_y,
                     vertical_wheel_delta, horizontal_wheel_delta):

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
