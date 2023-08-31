# ezmsg-gadget
__Griffin Milsap 2023__  
USB-gadget with HID control integration for Raspberry Pi (Zero/W/2W, 4, CM4)

* _Borrows heavily from [TinyPilot](https://github.com/tiny-pilot/tinypilot) -- Thank you!_  
* _HID inspiration from [Elmue at Codeproject](https://www.codeproject.com/Articles/1001891/A-USB-HID-Keyboard-Mouse-Touchscreen-emulator-with)_

# Purpose
Sometimes we want the capability to control other devices from an `ezmsg` system, and this module primarily exists to serve that purpose.  Installing this module onto a Raspberry Pi enables us to control virtual pointer and keyboards attached to any device with a USB port from within `ezmsg`

# Install

This library was created with Raspberry Pi devices in mind.  It may be possible to use this library with non-raspberry pi devices, but your mileage may vary!

1. At the bottom of your /boot/config.txt file, after `[all]`, add `dtoverlay=dwc2` to enable usb gadget mode.
2. 
    ``` bash
    git clone https://github.com/griffinmilsap/ezmsg-gadget.git
    pip install -e ./ezmsg-gadget
    sudo ezmsg-gadget install --service # Configures OS for ezmsg-gadget functionality
    sudo reboot
    ```

# Configuration
TODO: Notes on `dnsmasq`, ethernet 