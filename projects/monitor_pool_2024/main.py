# Initialize Watchdog Timer
from machine import reset, WDT, Timer, lightsleep
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer
from micropython import alloc_emergency_exception_buf
alloc_emergency_exception_buf(100)  # Print Exception Messages from Interrupts/Timers

# Import modules
from time import sleep_ms, localtime, ticks_ms, ticks_diff
import key_store
from wifi import WIFI
from webdis import WEBDIS
from thermocouple import THERMOCOUPLE
from epaper import EPAPER
from sys import exit, implementation
from collections import deque
#import TinyPICO_RGB as led


class PROJECT:
    def __init__(self):
        # Load modules in this Class
        self.thermocouple = THERMOCOUPLE()
        self.webdis_water = WEBDIS()
        self.webdis_air = WEBDIS()
        self.epaper = EPAPER()
        self.wifi = WIFI()

        self.uptime = ticks_ms()
        self.water_now = None
        self.air_now = None
        self.water_last = None
        self.air_last = None
        self.power_last = True
        self.display_lock = False

        self.water_deque = deque((),60)
        self.water_average = None
        
        if 'TinyS3' in implementation[2]:
            from tinys3 import get_vbus_present
            self.vbus = get_vbus_present             # type(vbus) is <class 'function'>
        elif 'TinyPICO' in implementation[2]:
            from machine import Pin                  # GPIO 9 is "Detect 5V Present"
            self.vbus = Pin(9, Pin.IN, Pin.PULL_UP)  # type(vbus) is <class 'Pin'>
        
        if key_store.get('webdis_key'):
            self.webdis_key = key_store.get('webdis_key')  # Webdis Water Temperature Data
        else:  # key_store values are empty
            self.webdis_key = input('Enter Webdis Key for storing Water Temp - ')
            key_store.set('webdis_key',self.webdis_key)
        self.wifi.connect()

    def check_power(self):
        '''Check if Power is connected to USB'''
        if not self.vbus():  # vbus() returns True/False (TinyS3) or 1/0 (TinyPICO)
            #led.solid(0,255,255) # Cyan
            if self.power_last:
                #led.solid(255,0,0) # Red
                #self.wifi.disconnect()
                self.display_lock = True
                self.epaper.update(power=False)
                sleep_ms(10000)
                self.display_lock = False
                self.power_last = False
            wdt.feed()
            #lightsleep(30000)
        else:
            #led.solid(255,255,0) # Yellow
            if not self.power_last:
                reset()
            else:
                self.power_last = True

    def check_reset(self):
        '''Reset and Clear Screen occasionally'''
        if ticks_diff(ticks_ms(), self.uptime) > 43200000:  # 12 hours
            reset()
    
    def check_wifi(self):
        '''Check if Wifi is still running'''
        if not self.wifi.isconnected() or not self.wifi.active():
            self.wifi.connect()

    def roundTraditional(self, val,digits):
        '''Rounding like you learned in Math'''
        return round(val+10**(-len(str(val))-1), digits)

    def water(self):
        '''Get water temperature reading from Thermocouple'''
        self.thermocouple.read()
        self.water_now = self.thermocouple.tempF
        self.water_deque.append(self.water_now)
        self.water_average = sum(self.water_deque)/len(self.water_deque)
    
    def send_to_webdis(self):
        '''Send current water temperature to Webdis'''
        self.webdis_water.timeseries(self.webdis_key,self.water_average)
        print(f'{self.water_average} sent to Webdis {self.webdis_water.webdis_json}')
    
    def air(self):
        '''Get current "Feels Like" Air temperature'''
        self.webdis_air.get('nws-feelslike')
        self.air_now = self.webdis_air.response_json
        print(f'Air Feels Like {self.air_now} F')
    
    def update_display(self):
        water_text = int(self.roundTraditional(self.water_average,0)) if type(self.water_average) is float else self.water_average  # str or None
        air_text   = int(self.roundTraditional(self.air_now,0))   if type(self.air_now)   is float else self.air_now    # str or None
        if (water_text is self.water_last) and (air_text is self.air_last):
            print('No Temperature Changes... Skipping Display Update')
        else:
            self.epaper.update(water=self.water_average, air=self.air_now)
        #print(f'Memory Free:   {int(gc.mem_free()/1024)}KB')
        self.water_last = self.water_average if not type(self.water_average) is float else int(self.roundTraditional(self.water_average,0))
        self.air_last   =   self.air_now if not type(self.air_now)   is float else int(self.roundTraditional(self.air_now,0))      


project = PROJECT()

print('Creating Sensor Loop Timer')
def sensor_loop_function(t):
    project.water()
t0 = Timer(0)
t0.init(period=5003, callback=sensor_loop_function)

print('Creating Webdis Timer')
def webdis_loop_function(t):
    if not project.display_lock:
        project.check_power()
    if project.wifi.isconnected():
        project.send_to_webdis()
t1 = Timer(1)
t1.init(period=10247, callback=webdis_loop_function)

print('Creating Display Update Timer')
def display_loop_function(t):
    if project.vbus():
        #led.solid(255,0,255) # Purple
        project.check_reset()
        project.check_wifi()
        project.air()
        project.display_lock = True
        project.update_display()
        project.display_lock = False
        wdt.feed()
t2 = Timer(2)
t2.init(period=180757, callback=display_loop_function)

print('Running functions on boot')
sensor_loop_function(0)
display_loop_function(0)


'''
###################################
# Run in thread, asyncio, loop, etc
###################################
print(f'project.tasks() running in {state} every {main_interval} seconds')
if state is 'thread':
    import _thread
    def main_loop():
        while True:
            project.tasks()
            sleep_ms(main_interval*1000)
    print('Launching Thread Loop')
    _thread.start_new_thread(main_loop,())
    
elif state is 'aiorepl':
    import asyncio
    import aiorepl
    async def main_loop():
        while True:
            project.tasks()
            await asyncio.sleep(main_interval)
    async def launch_coroutines():
        print("Launching Asyncio Coroutines...")
        task1 = asyncio.create_task(main_loop())
        repl = asyncio.create_task(aiorepl.task())
        await asyncio.gather(task1,repl)
    asyncio.run(launch_coroutines())

elif state is 'asyncio':
    import asyncio
    async def main_loop():
        project.tasks()
        await asyncio.sleep(main_interval)
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(main_loop())
    event_loop.run_forever()

elif state is 'timer':
    def timer_function(timer_main):
        project.tasks()
    timer_main = Timer(0)
    timer_function(timer_main)  # Initial Run on Boot
    timer_main.init(period=main_interval*1000, callback=timer_function)
    # View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

elif state is 'loop':
    while True:
        project.tasks()
        sleep_ms(main_interval*1000)

else:
    print(f'Unknown State: {state}')

# List of variables: dir()
# List of modules: help('modules')
# Time Commands: ntp()  time.localtime()  ntptime.settime()
'''
