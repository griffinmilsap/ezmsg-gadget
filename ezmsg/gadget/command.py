
import argparse

def cmdline() -> None:

    parser = argparse.ArgumentParser(
        description = "configuration"
    )

    args = parser.parse_args()

    # install, enumerate, remove_all require superuser permissions
    # Check for superuser

def install() -> None:
    # Add a systemd startup file
    # Add dwc, libcomposite to modules
    ...

def enumerate() -> None:
    # Arguments for mouse, keyboard, ethernet (and mac addresses)
    ...

def remove_all() -> None:
    # Remove all UDC functions and configs
    ...

def serve() -> None:
    # Serve HID endpoints
    ...

