from time import sleep_ms
from machine import reset, WDT, Timer
wdt = WDT(timeout=60000)  # Set 1-minute Hardware Watchdog Timer
main_interval = 5         # Time in seconds between Timer loops
state = 'loop'            # while 'loop' or 'timer'

from key_store import KEY_STORE
key_store = KEY_STORE()

from wifi import WIFI
wifi = WIFI()
wifi.connect()

from DFRobot_MicroPython_A02YYUW import DFRobot_A02_Distance
from send_to_influxdb import send_to_influxdb

class PROJECT:
    def __init__(self):
        self.ultrasonic = DFRobot_A02_Distance(rx=37)

    def control(self):
        values = []
        for i in range(5):
            values.append(self.ultrasonic.getDistance())
            sleep_ms(350) # minimum 300ms between device readings
        values.sort()
        self.distance = int(sum(values[1:4])/len(values[1:4]))
        #print(f'{self.distance}mm')
        if self.distance != 0:
            send_to_influxdb(field_name='mm',field_value=self.distance)
        

project = PROJECT()
def timer_function(timer_main):
    project.control()
    wdt.feed()


###################################
# Run with timer or lightsleep
###################################
if state is 'timer':
    print('main.py running in Timer')
    timer_main = Timer(0)
    timer_function(timer_main)  # Initial Run on Boot
    timer_main.init(period=main_interval*1000, callback=timer_function)
    # View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()
elif state is 'loop':
    print('main.py running in while True loop (Ctrl+C to REPL)')
    while True:
        timer_function(None)
        sleep_ms(main_interval*1000)
else:
    print(f'Unknown State: {state}')



