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
        self.aqi_average = None
        self.webdis_key = self.key_store.get('webdis_key')
        self.webdis_key_average = self.webdis_key + '-average'
        self.moving_average = deque((),60)  # 1-minute list of readings at 1 per second

    def read_loop(self):
        '''Continuous reads of UART data from PMS7003 Sensor (~1 per second)'''
        while True:
            if self.sensor.uart.any():
                self.data = self.sensor.read()

    def moving_average_loop(self):
        '''With deque 60 and Timer Period 5 this should be about a 5-minute moving average'''
        self.aqi = self.calculate.aqi(self.data['PM2_5_ATM'],self.data['PM10_0_ATM'])
        self.moving_average.append(self.aqi)
        self.aqi_average = sum(self.moving_average)/len(self.moving_average)
                
    def webdis_loop(self):
        '''Timer loop that sends current sensor data to Webdis/Redis'''
        try:
            self.webdis.timeseries(self.webdis_key_average,self.aqi_average)
            wdt.feed()
        except:
            pass
        
        
project = PROJECT()

print('Launching continuous UART sensor read loop in Thread')
sleep(1)
_thread.start_new_thread(project.read_loop,())
sleep(1)

print('Creating Moving Average Timer')
def moving_average_loop_function(t0):
    project.moving_average_loop()
t0 = Timer(0)
t0.init(period=5000, callback=moving_average_loop_function)

print('Creating Webdis Timer')
def webdis_loop_function(t1):
    project.webdis_loop()
t1 = Timer(1)
t1.init(period=30000, callback=webdis_loop_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

print()
print('='*45)
print('Useful Commands:')
print('  project.data')
print('  project.aqi')
print('  project.aqi_average')
print('  project.webdis_key')
print('  project.webdis.webdis_json')
print('  project.sensor.uart')
print('  project.wifi.isconnected()')
print('  timer_main.value()')
print('='*45)
print()

