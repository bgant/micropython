# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=180000)  # Hardware Watchdog Timer

from time import sleep
import _thread
from collections import deque

from key_store import KEY_STORE
from wifi import WIFI
from webdis import WEBDIS
from pms7003 import Pms7003
from aqi import AQI


class PROJECT:
    def __init__(self):
        self.sensor = Pms7003(uart=1)  # rx=9 tx=10 by default (project.sensor.uart)
        self.calculate = AQI()
        self.key_store = KEY_STORE()
        self.wifi = WIFI()
        self.wifi.connect()
        self.webdis = WEBDIS()
        self.data = None
        self.aqi = None
        self.webdis_key = self.key_store.get('webdis_key')
        self.moving_average = deque((),60)  # 1-minute list of readings at 1 per second

    def read_loop(self):
        '''Continuous reads of UART data from PMS7003 Sensor (~1 per second)'''
        while True:
            if self.sensor.uart.any():
                self.data = self.sensor.read()
                self.aqi = self.calculate.aqi(self.data['PM2_5_ATM'],self.data['PM10_0_ATM'])
                self.moving_average.append(self.aqi)
                
    def webdis_loop(self):
        '''Timer loop that sends current sensor data to Webdis/Redis'''
        self.webdis.timeseries(self.webdis_key,self.aqi)
        wdt.feed()
        
project = PROJECT()

print('Launching continuous UART sensor read loop')
sleep(1)
_thread.start_new_thread(project.read_loop,())
sleep(1)

def timer_function(timer_main):
    project.webdis_loop()
timer_main = Timer(0)
main_interval=30  # Seconds between Webdis Send
print(f'Creating {main_interval} second Timer to send AQI to {project.webdis_key}')
timer_main.init(period=main_interval*1000, callback=timer_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

print()
print('='*45)
print('Useful Commands:')
print('  project.data')
print('  project.aqi')
print('  project.webdis_key')
print('  project.webdis.webdis_json')
print('  project.sensor.uart')
print('  project.wifi.isconnected()')
print('  timer_main.value()')
print('='*45)
print()

