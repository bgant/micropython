from machine import reset
import pool_display
import pool_wifi
import pool_thermocouple

# Rounding the way you expect in Math
def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)

water_now  = None
air_now    = None
water_last = None
air_last   = None

def main(timer):
    global water_last
    global air_last
    global water_now
    global air_now
    water_now = pool_thermocouple.temp()
    gc.collect()
    air_now   = pool_wifi.download_weather()
    power_now = True  # Placeholder
    if not (( int(roundTraditional(water_now,0)) is water_last ) and ( int(roundTraditional(air_now,0)) is air_last)):
        pool_display.update(water=water_now, air=air_now, power=power_now)
    else:
        print('No Temperature Changes... Skipping Display Update...')
    print('='*45)
    print()
    water_last = None if water_now is None else int(roundTraditional(water_now,0))
    air_last = None if air_now is None else int(roundTraditional(air_now,0))

# ESP32 has four hardware timers to choose from (0 through 3)
from machine import Timer
timer = Timer(0)
main(timer) # Initial Run on Boot
timer.init(period=600000, mode=Timer.PERIODIC, callback=main)
# View Timer value: timer.value()   Stop Timer: timer.deinit()
# List of variables: dir()
# Time Commands: ntp()  time.localtime()  ntptime.settime()


    
