'''

def main():

    water_now = pool_water()
    air_now   = pool_wifi(water_temp=water_now)

    if not (( water_now is water_last ) and ( air_now is air_last)):
        pool_display(water=water_now, air=air_now)

    water_last = water_now
    air_last   = air_last

    watchdog feed


def power_off():
    check display busy
    clear dislplay
    display power off symbol
    put device in sleep mode

Interrupt if IO9 VBUS 'Detect 5V Present' goes low and run power_off function

Timer every 10 minutes runs main

'''

