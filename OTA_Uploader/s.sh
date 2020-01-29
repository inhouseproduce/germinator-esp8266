#!/bin/sh

ampy --port /dev/tty.SLAB_USBtoUART put main.py
ampy --port /dev/tty.SLAB_USBtoUART put micropython-ota-updater
ampy --port /dev/tty.SLAB_USBtoUART put main