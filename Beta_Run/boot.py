import machine
import sht31

# SHT31 Pin Init
i = machine.I2C(sda=machine.Pin(5), scl=machine.Pin(4))
s = sht31.SHT31(i)

# 2 Relay Module Pin Init
heaterPin = machine.Pin(0, machine.Pin.OUT)
humidiPin = machine.Pin(2, machine.Pin.OUT)
