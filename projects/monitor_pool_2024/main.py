# Initialize Watchdog Timer
from machine import reset, WDT, Timer, lightsleep
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer
main_interval = 450        # Time in seconds between loops (loop takes 90 seconds)
state = 'timer'            # while 'loop' or 'timer'

# Import modules
from time import sleep_ms, localtime, ticks_ms, ticks_diff
from key_store import KEY_STORE
from wifi import WIFI
from webdis import WEBDIS
from thermocouple import THERMOCOUPLE
from epaper import EPAPER
from sys import implementation


class PROJECT:
    def __init__(self):
        # Load modules in this Class
        self.key_store = KEY_STORE()
        self.wifi = WIFI()
        self.wifi.connect()
        self.webdis = WEBDIS()
        self.thermocouple = THERMOCOUPLE()
        self.epaper = EPAPER()
        
        self.uptime = ticks_ms()
        self.water_now = None
        self.air_now = None
        self.water_last = None
        self.air_last = None
        self.power_last = True
        
        if 'TinyS3' in implementation[2]:
            from tinys3 import get_vbus_present
            self.vbus = get_vbus_present  # type(vbus) is <class 'function'>
        elif 'TinyPICO' in implementation[2]:
            from machine import Pin       # GPIO 9 is "Detect 5V Present"
            self.vbus = Pin(9, Pin.IN)    # type(vbus) is <class 'Pin'>
        
        if self.key_store.get('webdis_key'):
            self.webdis_key = self.key_store.get('webdis_key')  # Webdis Water Temperature Data
        else:  # key_store values are empty
            self.webdis_key = input('Enter Webdis Key for storing Water Temp - ')
            self.key_store.set('webdis_key',self.webdis_key)

    def check_power(self):
        '''Check if Power is connected to USB'''
        if not self.vbus():  # vbus() returns True/False (TinyS3) or 1/0 (TinyPICO)
            if self.power_last:
                self.wifi.disconnect()
                self.epaper.update(power=False)
                self.epaper.epd.ReadBusy()
                sleep_ms(2000)
                self.power_last = False
            wdt.feed()
            lightsleep(30000)
            return None
        else:
            print('Power is connected')

    def check_reset(self):
        '''Reset and Clear Screen occasionally'''
        if ticks_diff(ticks_ms(), self.uptime) > 43200000:  # 12 hours
            reset()
        else:
            print('No Reset needed')
    
    def check_wifi(self):
        '''Check if Wifi is still running'''
        if not self.wifi.isconnected() or not self.wifi.active():
            wifi.connect()
        else:
            print('Wifi is connected')

    def roundTraditional(self, val,digits):
        '''Rounding like you learned in Math'''
        return round(val+10**(-len(str(val))-1), digits)

    def water(self):
        '''Get water temperature reading from Thermocouple'''
        self.thermocouple.read()
        self.water_now = self.thermocouple.tempF
    
    def send_to_webdis(self):
        '''Send current water temperature to Webdis'''
        self.webdis.timeseries(self.webdis_key,self.water_now)
        print(f'{self.water_now} sent to Webdis {self.webdis.webdis_json}')
    
    def air(self):
        '''Get current "Feels Like" Air temperature'''
        self.webdis.get('nws-feelslike')
        self.air_now = self.webdis.response_json
        print(f'Air Feels Like {self.air_now} F')
    
    def update_display(self):
        water_text = int(self.roundTraditional(self.water_now,0)) if type(self.water_now) is float else self.water_now  # str or None
        air_text   = int(self.roundTraditional(self.air_now,0))   if type(self.air_now)   is float else self.air_now    # str or None
        if (water_text is self.water_last) and (air_text is self.air_last):
            print('No Temperature Changes... Skipping Display Update')
        else:
            self.epaper.update(water=self.water_now, air=self.air_now)
        #print(f'Memory Free:   {int(gc.mem_free()/1024)}KB')
        
    def cleanup(self):
        '''End of loop cleanup'''
        self.water_last = self.water_now if not type(self.water_now) is float else int(self.roundTraditional(self.water_now,0))
        self.air_last   =   self.air_now if not type(self.air_now)   is float else int(self.roundTraditional(self.air_now,0))
        self.power_last = True        
        
    def tasks(self):
        '''Main Tasks to Perform'''
        self.check_power()
        self.check_reset()
        self.check_wifi()
        self.water()
        self.send_to_webdis()
        self.air()
        self.update_display()
        self.cleanup()
        wdt.feed()
        

project = PROJECT()

# This seems to be the best way to run loop and access REPL
import _thread
def main_loop():
    while True:
        project.tasks()
        sleep_ms(60000)

print('Launching Thread Loop')
_thread.start_new_thread(main_loop,())


'''
import asyncio
import aiorepl

async def main_loop():
    while True:
        project.tasks()
        await asyncio.sleep(60)
    
async def launch_coroutines():
    print("Launching Asyncio Coroutines...")
    task1 = asyncio.create_task(main_loop())
    repl = asyncio.create_task(aiorepl.task())
    await asyncio.gather(task1,repl)

asyncio.run(launch_coroutines())
'''

'''No access to REPL
import asyncio

async def something():
    project.loop()
    await asyncio.sleep(180)

event_loop = asyncio.get_event_loop()
event_loop.create_task(something())
event_loop.run_forever()
'''
 
'''
###################################
# Run in timer or loop
###################################
print()
if state is 'timer':
    print(f'main.py running in Timer every {main_interval} seconds')
    timer_main = Timer(0)
    timer_function(timer_main)  # Initial Run on Boot
    timer_main.init(period=main_interval*1000, callback=timer_function)
    # View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()
elif state is 'loop':
    print('main.py running in while True loop every {main_interval} seconds (Ctrl+C to REPL)')
    while True:
        timer_function(None)
        sleep_ms(main_interval*1000)
else:
    print(f'Unknown State: {state}')


# List of variables: dir()
# List of modules: help('modules')
# Time Commands: ntp()  time.localtime()  ntptime.settime()
'''