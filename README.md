# ezmsg-hid
__Griffin Milsap 2023__  
USB-gadget HID control integration for Raspberry Pi (Zero/W/2W, 4, CM4)

_Borrows heavily from [TinyPilot](https://github.com/tiny-pilot/tinypilot) -- Thank you!_

# Install
``` bash
git clone https://github.com/griffinmilsap/ezmsg-hid.git
pip install -e ./ezmsg-hid
sudo ezmsg-hid-install # Adds USB Gadget service/scripts, and reboots
```