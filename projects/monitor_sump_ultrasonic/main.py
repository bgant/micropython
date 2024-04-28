from time import sleep_ms
from machine import reset, WDT, Timer
wdt = WDT(timeout=60000)  # Set 1-minute Hardware Watchdog Timer
main_interval = 2         # Time in seconds between Timer loops
state = 'loop'            # while 'loop' or 'timer'

from key_store import KEY_STORE
key_store = KEY_STORE()

from wifi import WIFI
wifi = WIFI()
wifi.connect()

import urequests
from DFRobot_MicroPython_A02YYUW import DFRobot_A02_Distance

class PROJECT:
    def __init__(self):
        self.ultrasonic = DFRobot_A02_Distance(rx=37)
        self.webdis_host = key_store.get('webdis_host')
        self.webdis_port = key_store.get('webdis_port')
        if key_store.get('webdis_key'):
            self.webdis_key = key_store.get('webdis_key')  # Webdis Key Name
        else:  # key_store value is empty
            self.webdis_key = input('Enter Webdis Key Name - ')
            key_store.set('webdis_key',self.webdis_key)
            
    def control(self):
        distance = self.ultrasonic.getDistance()
        #print(f'{distance}mm')
        if distance != 0:
            URL = f'http://{self.webdis_host}:{self.webdis_port}/TS.ADD/{self.webdis_key}/*/{distance}'
            response = urequests.get(URL)
            print(f'Webdis Response: {response.text}')
        

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
