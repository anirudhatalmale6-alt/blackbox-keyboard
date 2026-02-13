#!/usr/bin/env python3
import smbus
from time import sleep

addr = 0x27
bus = smbus.SMBus(6)
BL = 0x08
EN = 0x04

def strobe(d):
    bus.write_byte(addr, d | EN | BL)
    sleep(0.0005)
    bus.write_byte(addr, (d & ~EN) | BL)
    sleep(0.0001)

def cmd4(d):
    bus.write_byte(addr, d | BL)
    strobe(d)

def cmd(c):
    cmd4(c & 0xF0)
    cmd4((c << 4) & 0xF0)

cmd4(0x30); cmd4(0x30); cmd4(0x30); cmd4(0x20)
cmd(0x28); cmd(0x0C); cmd(0x01); cmd(0x06)
sleep(0.2)
print("LCD cleared")
