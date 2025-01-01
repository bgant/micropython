from time import sleep_ms
from machine import reset, WDT, Timer, Pin
wdt = WDT(timeout=180000)  # Set 3-minute Hardware Watchdog Timer
main_interval = 60         # Time in seconds between Timer loops
state = 'timer'            # while 'loop' or 'timer'

import key_store

from wifi import WIFI
wifi = WIFI()
wifi.connect()

from webdis import WEBDIS
webdis = WEBDIS()

import uping

class PROJECT:
    def __init__(self):
        key_store.enable()
        if key_store.get('sensor_pin'):
            self.sensor_pin = key_store.get('sensor_pin')
        else:
            self.sensor_pin = input('Enter Sensor Pin - ')  # 2.5V Input Pin (any GPIO pin should work)
            key_store.set('sensor_pin',self.sensor_pin)
        self.power = Pin(int(self.sensor_pin), Pin.IN)

        if key_store.get('webdis_key'):
            self.webdis_key = key_store.get('webdis_key')  # Webdis Key Name
        else:  # key_store value is empty
            self.webdis_key = input('Enter Webdis Key Name - ')
            key_store.set('webdis_key',self.webdis_key)
        key_store.close()  # Close database and file when finished using it

    def network_fail(self):
        print('Unable to access network... resetting...')
        sleep_ms(15000)
        reset()

    def ping_check(self, target):
        try:
            pong = uping.ping(target,quiet=True)
            if not pong[1]:  # Zero packets received
                self.network_fail()
        except:
            self.network_fail()
            
    def control(self):
        self.ping_check(wifi.gateway)
        webdis.timeseries(self.webdis_key,self.power.value())
        print(webdis.response_text,self.webdis_key,self.power.value())


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
