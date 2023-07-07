from machine import reset, WDT, lightsleep
wdt = WDT(timeout=780000)  # Set 13-minute Hardware Watchdog Timer

from time import sleep
import pool_display
import pool_wifi
import pool_thermocouple
from client_id import client_id

# Rounding the way you expect in Math
def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)

water_now  = None
air_now    = None
water_last = None
air_last   = None

while True:
    # Collect Data:
    power_now = True  # Placeholder for checking VBUS Pin(33)
    water_now = pool_thermocouple.temp()
    if pool_wifi.wlan.isconnected():
        gc.collect()
        air_now   = pool_wifi.download_weather()
    else:
        print('Wifi Not Connected... Reconnecting...')
        pool_wifi.wlan_connect(pool_wifi.ssid_name,pool_wifi.ssid_pass)
        gc.collect()
        air_now   = pool_wifi.download_weather()

    # Update Display:
    if type(water_now) is str:  # Fault string
        pool_display.update(water=water_now, air=air_now, power=power_now)
    elif (int(roundTraditional(water_now,0)) is not water_last) or (int(roundTraditional(air_now,0)) is not air_last):
        pool_display.update(water=water_now, air=air_now, power=power_now)
    else:
        print('No Temperature Changes... Skipping Display Update...')
    print('='*45)
    print()
    
    # Cleanup at end of loop:
    water_last = None if ( water_now is None ) or ( type(water_now) is str ) else int(roundTraditional(water_now,0))
    air_last = None if air_now is None else int(roundTraditional(air_now,0))
    wdt.feed()
    print('Going to sleep now...')
    sleep(2)
    lightsleep(600000)

# Reset Every once in a while to Clear Screen:
def reset_device(timer_reset):
    reset()
timer_reset = Timer(1)
timer_reset.init(period=7200000, mode=Timer.PERIODIC, callback=reset_device)
# View Timer value: timer_reset.value()   Stop Timer: timer_reset.deinit()

# List of variables: dir()
# List of modules: help('modules')
# Time Commands: ntp()  time.localtime()  ntptime.settime()
