# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=180000)  # Hardware Watchdog Timer

from time import sleep
from collections import deque

from key_store import KEY_STORE
from wifi import WIFI
from webdis import WEBDIS
from pms7003 import Pms7003
from aqi import AQI


class PROJECT:
    def __init__(self):
        self.wifi = WIFI()
        self.wifi.connect()

        self.data = None
        self.aqi = None
        self.aqi_average = None
        self.moving_average = deque((),60)  # 1-minute list of readings at 1 per second

        self.key_store = KEY_STORE()
        self.webdis_key = self.key_store.get('webdis_key')
        self.webdis_key_average = self.webdis_key + '-average'
        self.key_store.db.close()
        
        self.webdis = WEBDIS()
        self.sensor = Pms7003(uart=1)  # rx=9 tx=10 by default (project.sensor.uart)
        self.calculate = AQI()
        
    def read_loop(self):
        '''UART data from PMS7003 Sensor (updates~1 per second)'''
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
            wdt.feed()  # This should only run if Webdis line above is success
        except:
            pass
        
        
project = PROJECT()

print('Creating Read Loop Timer')
def read_loop_function(t0):
    project.read_loop()
t0 = Timer(0)
t0.init(period=3000, callback=read_loop_function)

print('Creating Moving Average Timer')
def moving_average_loop_function(t1):
    project.moving_average_loop()
t1 = Timer(1)
t1.init(period=5000, callback=moving_average_loop_function)

print('Creating Webdis Timer')
def webdis_loop_function(t2):
    project.webdis_loop()
t2 = Timer(2)
t2.init(period=30000, callback=webdis_loop_function)
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
print("  project.webdis.get('foo')")
print('='*45)
print()

