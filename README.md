# ezmsg-gadget
__Griffin Milsap 2023__  

USB-gadget with HID control integration for Raspberry Pi (Zero/W/2W, 4, CM4)

* _Borrows heavily from [TinyPilot](https://github.com/tiny-pilot/tinypilot) -- Thank you!_  
* _HID inspiration from [Elmue at Codeproject](https://www.codeproject.com/Articles/1001891/A-USB-HID-Keyboard-Mouse-Touchscreen-emulator-with)_

# Purpose
Sometimes we want the capability to control other devices from an `ezmsg` system, and this module primarily exists to serve that purpose.  Installing this module onto a Raspberry Pi enables us to control virtual pointer and keyboards attached to any device with a USB port from within `ezmsg`.  It does this by using USB gadget mode and HID (Human Interface Device) compliant device descriptors.

_Hey!  Want to do all this, but __wirelessly__ with Bluetooth? Check out [ezmsg-bthid](https://github.com/griffinmilsap/ezmsg-bthid)_

# Install
This library was created with Raspberry Pi devices in mind.  It may be possible to use this library with non-raspberry pi devices, but your mileage may vary!

1. At the bottom of your `/boot/config.txt` (`/boot/firmware/config.txt` for recent RPi OSes) file, after `[all]`, add `dtoverlay=dwc2` to enable usb gadget mode.
    1. __CM4 NOTE__: According to the [Raspberry Pi Forums](https://forums.raspberrypi.com/viewtopic.php?t=347459), on a Raspberry Pi Compute Module 4 you'll need to:
        1. Comment any lines that contain `otg_mode=1`
        1. Comment any lines that contain `dtoverlay=dwc2`
        1. Instead, add the following at the end of config.txt:
            ```
            [all]
            dtoverlay=dwc2,dr_mode=peripheral
            ```
2. Run the following commands:
    ```
    $ sudo apt install python3-venv
    $ sudo su
    # python3 -m venv /opt/ezmsg-gadget
    # source /opt/ezmsg-gadget/bin/activate
    (ezmsg-gadget-env) # pip install --upgrade pip
    (ezmsg-gadget-env) # pip install git+https://github.com/griffinmilsap/ezmsg-gadget.git
    (ezmsg-gadget-env) # ezmsg-gadget install -y
    # reboot
    ```
Note that in the script above, ezmsg-gadget is installed to a special virtual environment in `/opt`.  This is because `ezmsg-gadget activate` must be executed as `root`, and the `systemd` service files that the installer places involve running code from `ezmsg-gadget` _as root during boot_.  

## Uninstall
```
sudo /opt/ezmsg-gadget/bin/ezmsg-gadget uninstall
```

# Usage
__`ezmsg-gadget` has two functions:__
1. Set up the ConfigFS within the USB gadget specification to provide "functions"
2. Provide an endpoint that connects to a remote `ezmsg` GraphServer and sets up topics for sending HID messages to control the host PC using virtual USB HID devices.

Once installed, these functions can be activated and controlled with a command-line entrypoint: `ezmsg-gadget`

```
$ ezmsg-gadget --help
usage: ezmsg-gadget [-h] [--config CONFIG] [--install-endpoint-service] [--no-boot-service] [--yes]
                    {activate,deactivate,install,uninstall,endpoint}

config and control

positional arguments:
  {activate,deactivate,install,uninstall,endpoint}

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        config file for gadget settings. default: /etc/ezmsg-gadget.conf
  --install-endpoint-service
                        install a service to launch 'ezmsg-gadget endpoint' on boot
  --no-boot-service     don't install a boot service for 'ezmsg-gadget activate'
  --yes, -y             yes to all questions for interactive install/uninstall
```

The first function is something that generally requires superuser priveliges on most Linux systems, and running Python scripts as superuser comes with a host of issues.  Nonetheless, this module has an installer to set up the appropriate OS configuration and has functionality to add kernel modules dynamically.  This module is intended to run one short-lived `activate` function as superuser which sets up the USB gadget and HID file descriptors -- and even has a setup script that will add a `systemd` service unit to do this automatically on boot.

The second function can be run in user-space without superuser permissions once the USB gadget is activated.  Because this module will generally be deployed on headless single-board-computers (like the Raspberry Pi Zero W series), the module installer will also set up a service to launch `ezmsg-gadget endpoint` for you on boot, which attempts to connect to a remote ezmsg GraphServer running at the hostname specified in the ezmsg-gadget configuration file.

# Configuration
This is a somewhat complicated extension and requires some extra configuration to achieve maximum utility.  

The configuration of this module can be done using `/etc/ezmsg-gadget.conf` which has the following format:
``` ini
# configuration for ezmsg-gadget
[gadget]
name = g1

[endpoint]
# ezmsg-gadget has optional distributed ezmsg functionality
# to spin up a service that connects to a remote graphserver
# and exposes topics for HID-gadget manipulation
remote_host = localhost
remote_port = 25978

# function section format is [function.[Class].[name]]
# * [Class] will resolve to ezmsg.gadget.function.Class 
#     * note that this is case sensitive; most Python
#       classes are capitalized
# * although this format allows defining multiple functions
#   with the same [name], it will not function
[function.Keyboard.keyboard0]
# US Keyboard

[function.Mouse.mouse0]
# Relative movement mouse

[function.Ethernet.usb0]
# some functions have additional parameters that you can
# add in the section here
host_addr = 60:6D:3C:3E:0C:7B
dev_addr = 60:6D:3C:3E:0C:6B

# any files in an associated *.d directory will also be loaded
```

## Ethernet Setup
One of the available functions this extension can enable is a virtual ethernet device.  By default, this will enumerate locally as `usb0` and on a fresh install of raspbian, it will come up with a link-local address.  

### Static IP
It can be handy to assign a static IP address to this new interface.  To do this:
1. Create the following file as `/etc/network/interfaces.d/usb0`
    ```
    auto usb0
    allow-hotplug usb0
    iface usb0 inet static
        address 10.55.0.1
        netmask 255.255.255.248
    ```
    __OR if you're rolling an OS using netplan (Ubuntu)__
    Create the following file as `/etc/netplan/99_usb0.yaml`
    ```
    network:
        version: 2
        renderer: networkd
        ethernets:
          usb0:
            addresses:
              - 10.55.0.1/29
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
    NOTE: Ubuntu server runs its own service on port 53 you'll need to disable to run dnsmasq:
    ```
    sudo systemctl disable systemd-resolved
    sudo systemctl stop systemd-resolved
    ```   
    __Pro Tip__: The IP address leases that `dnsmasq` creates can be found in `/var/lib/misc/dnsmasq.leases`.  This will tell you exactly which of the IP addresses corresponds to your USB host device.

### MAC Address Selection
The virtual ethernet device allows us to define our own MAC address for the ethernet adapter, and not all MAC addresses are created equal.  The host and device MAC Address must have two least-significant bits of the first octet clear `(XXXXXX00)` for most purposes.
* The least significant bit as 0 indicates that this is a unicast MAC address (not multicast)
* The second to least significant bit indicates that this is a Universal MAC address (not locally administrated) -- This is important for naming purposes; __when this bit is 0, Android assigns `ethX` instead of `usbX` to the device__ which is important because Android currently ignores any ethernet devices that enumerate as `usbX`. 
    * __Pro Tip__: It also appears that stock smartphone Android builds ignore attached ethernet devices that don't provide outbound internet access.  While it is possible to set up the USB device to act as a router and provide outbound internet access to the smartphone with IP forwarding, this is likely to result in VERY slow internet connectivity and completely hamstring your mobile device's internet speeds.  You can still use your virtual ethernet device to communicate with these devices, but you'll need to _turn off your device's wifi and mobile data_ to enable communication with local IP addresses.


