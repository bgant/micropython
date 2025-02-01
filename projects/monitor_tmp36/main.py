# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=180000)  # 3 Minute Hardware Watchdog Timer
main_interval = 10         # Time in seconds between loops
state = 'timer'            # while 'loop' or 'timer'

# Load key_store/secrets
import key_store

# Connect to Wifi and set Clock
from wifi import WIFI
wifi = WIFI()
wifi.connect()

# Import Project specific modules
import AnalogDevices_TMP36 as tmp36
from webdis import WEBDIS
import uping


class PROJECT:
    def __init__(self):
        self.ADC_PIN = 37
        self.webdis_key = "webdis-ryan-temp1"
        self.webdis = WEBDIS()
        
    def read_temp(self):
        '''Read Analog Devices TMP36 Temperature Probe'''
        return tmp36.read_temp(self.ADC_PIN)
    
    def send_to_webdis(self):
        '''Send current temperature to Webdis'''
        tempF = str(self.read_temp())
        self.webdis.timeseries(self.webdis_key,tempF)
        print(f'{tempF} sent to Webdis {self.webdis.webdis_json}')
    
    def ping_check(self, target):
        try:
            pong = uping.ping(target,quiet=True)
            if not pong[1]:  # Zero packets received
                self.network_fail()
        except:
            self.network_fail()
    
    def network_fail(self):
        print('Unable to access network... resetting...')
        from time import sleep
        sleep(20)
        reset()


project = PROJECT()

def timer_function(timer_main):
    project.ping_check(wifi.gateway)
    project.send_to_webdis()
    wdt.feed()


###################################
# Run in timer or loop
###################################
if state is 'timer':
    print('main.py running in Timer')
    timer_main = Timer(0)
    timer_function(timer_main)  # Initial Run on Boot
    timer_main.init(period=main_interval*1000, callback=timer_function)
    # View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()
elif state is 'loop':
    print('main.py running in while True loop (Ctrl+C to REPL)')
    from time import sleep_ms
    while True:
        timer_function(None)
        sleep_ms(main_interval*1000)
else:
    print(f'Unknown State: {state}')

