from time import sleep_ms
from machine import reset, WDT, Timer, Pin
wdt = WDT(timeout=120000)  # Set 2-minute Hardware Watchdog Timer
main_interval = 60         # Time in seconds between Timer loops
state = 'timer'            # while 'loop' or 'timer'

from key_store import KEY_STORE
key_store = KEY_STORE()

from wifi import WIFI
wifi = WIFI()
wifi.connect()

from webdis import WEBDIS
webdis = WEBDIS()

class PROJECT:
    def __init__(self):
        self.power = Pin(37, Pin.IN)   # 2.5V Input Pin (any GPIO pin should work)
        if key_store.get('webdis_key'):
            self.webdis_key = key_store.get('webdis_key')  # Webdis Key Name
        else:  # key_store value is empty
            self.webdis_key = input('Enter Webdis Key Name - ')
            key_store.set('webdis_key',self.webdis_key)

    def control(self):
        webdis.timeseries(self.webdis_key,self.power.value())


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
