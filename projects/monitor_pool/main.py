from machine import reset, WDT, Timer
wdt = WDT(timeout=780000)  # Set 13-minute Hardware Watchdog Timer

from time import sleep
import pool_display
import pool_wifi
import pool_thermocouple
from client_id import client_id

# Rounding the way you expect in Math
def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)

# Global Values outside of main(timer_main) loop function:
water_now  = None
air_now    = None
water_last = None
air_last   = None

# Main loop:
def main(timer_main):
    global water_last
    global air_last
    global water_now
    global air_now
    
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

# Run main loop through Timer to retain access to the REPL:
timer_main = Timer(0)
main(timer_main) # Initial Run on Boot
timer_main.init(period=600000, mode=Timer.PERIODIC, callback=main)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

# Reset Every 12 hours to Clear Screen:
def reset_device(timer_reset):
    reset()
timer_reset = Timer(1)
timer_reset.init(period=43200000, mode=Timer.PERIODIC, callback=reset_device)

# List of variables: dir()
# List of modules: help('modules')
# Time Commands: ntp()  time.localtime()  ntptime.settime()
