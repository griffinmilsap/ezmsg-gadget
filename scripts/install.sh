#!/usr/bin/env bash

# ACTUALLY this should be an install entrypoint for the module
# THat way we can pip install the package then run something like ezmsg-hid-install

sudo su

# TODO
# echo "dtoverlay=dwc2" > sudo tee -a /boot/config.txt

# Install dnsmasq

# Copy fs into root file system
# systemctl daemon-reload
# systemctl enable gadget.service

# reboot
