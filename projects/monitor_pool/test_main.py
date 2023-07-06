'''

import tinypico
tinypico.set_dotstar_power(False)


def main():

    water_now = pool_water()
    air_now   = pool_wifi(water_temp=water_now)

    if not (( water_now is water_last ) and ( air_now is air_last)):
        pool_display(water=water_now, air=air_now)

    <do we do anything if both water_now and air_now are None?>
    <if water_now is None doesn't that mean the probe is broken?>
    <display 'ERROR' if water_now is None?>

    water_last = water_now
    air_last   = air_last

    watchdog feed

    tinypico.go_deepsleep(ms) or machine.deepsleep(ms) which effectively performs a hard reset on wake
    machine.lightsleep(ms) to preserve RAM and networking (execution resumed from the point sleep was requested) so no need for Timer or main() function


def power_off():
    check display busy
    clear dislplay
    display power off symbol
    put device in sleep mode

Interrupt if IO9 VBUS 'Detect 5V Present' goes low and run power_off function

Timer every 10 minutes runs main

'''
