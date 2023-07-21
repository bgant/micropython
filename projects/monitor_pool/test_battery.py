from machine import Pin, reset, WDT
wdt = WDT(timeout=15000)
import TinyPICO_RGB as led
from tinypico import get_battery_voltage

while True:
    if  get_battery_voltage() >= 3.7:
        led.blink(0,255,0)
    elif get_battery_voltage() < 3.7:
        led.blink(255,0,0)
    else:
        led.blink(0,0,255)
    wdt.feed()
