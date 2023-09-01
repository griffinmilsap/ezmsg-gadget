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
This is a somewhat complicated extension and requires some extra configuration to achieve maximum utility.

## Ethernet
One of the available gadget devices this extension can create is a virtual ethernet device.  By default, this will enumerate as usb0 and on a fresh install of raspbian, it will come up with a link-local address.  

### Static IP
It can be handy to assign a static IP address to this new interface.  To do this:
1. Create the following file as `/etc/network/interfaces.d`
    ```
    auto usb0
    allow-hotplug usb0
    iface usb0 inet static
        address 10.55.0.1
        netmask 255.255.255.248
    ```
    This will ensure that whenever the usb0 ethernet device becomes available, it will automatically be brought up and will have the statically assigned IP address of `10.55.0.1`.

### DHCP/DNS
The major use case of an ethernet gadget device here is for direct wired communications with the host USB device.  To support this, it can be helpful to configure a mini DHCP server to run on the Raspberry Pi that can assign the host a suitable IP address and act as a name server.  This can be accomplished by installing and configuring `dnsmasq` as follows:
1. Install `dnsmasq`
    ```
    sudo apt install dnsmasq
    ```
2. Create the following file as `/etc/dnsmasq.d/usb0.conf`
    ``` bash
    interface=usb0
    dhcp-range=10.55.0.2,10.55.0.6,255.255.255.248,1h
    dhcp-option=option:router
    dhcp-option=option:dns-server
    dhcp-authoritative
    leasefile-ro
    ```
    This will run dnsmasq on startup, and sets up the server to assign IP addresses from `10.55.0.2-6`, ensuring that your USB Host will sit at some IP address within that range.  
    __Pro Tip__: The IP address leases that `dnsmasq` creates can be found in `/var/lib/misc/dnsmasq.leases`.  This will tell you exactly which of the IP addresses corresponds to your USB host device.

### MAC Address Selection
MAC Address must have two least-significant bits of the first octet clear `(XXXXXX00)`
The least significant bit as 0 indicates that this is a unicast MAC address (not multicast)
The second to least significant bit indicates that this is a Universal MAC address (not locally administrated) -- This is important for naming purposes; when this bit is 0, Android assigns `ethX` instead of `usbX` to the device


