###################################
# Built-in Modules: help('modules')
###################################
from machine import Pin, SPI
from time import sleep_ms
from sys import implementation


###################################
# 3rd-Party Modules on Github
###################################
# mpremote a0 mip install --target= github:eliotb/micropython-max31856/max31856.py
from max31856 import Max31856
from key_store import KEY_STORE

class THERMOCOUPLE:
    def __init__(self):
        '''Max31856 Settings'''
        tc_type = 'K'  # K-Type Thermocouple
        self.spi = SPI(1)   # Shared SPI with Waveshare Display
        if 'TinyPICO' in implementation[2]:
            self.cs = Pin(33, Pin.OUT)  # Assign device its own chip select (CS) pin
        elif 'TinyS3' in implementation[2]:
            self.cs = Pin(6, Pin.OUT)   # Assign device its own chip select (CS) pin
        else:
            self.cs = Pin(6, Pin.OUT)   # Assign device its own chip select (CS) pin
        self.max31856 = Max31856(self.spi, self.cs, tc_type)
        
        key_store = KEY_STORE()
        if key_store.get('thermocouple_adjustment'):
            self.adjustment = float(key_store.get('thermocouple_adjustment'))  # Temperature (C) adjustment from test with Thermometers
        else:
            self.adjustment = 0.0
        key_store.db.close()

    def read(self):
        '''Read Thermocouple Temperature'''
        try:
            self.cs(0)  # Select Shared SPI Peripheral
            self.spi.init(phase=1)  # Waveshare uses phase=0 and MAX31856 uses phase=1
            attempts = 5  # Number of tries
            #print(f'Taking {attempts} temperature readings to average...')
            readings = []
            while attempts:
                data = self.max31856.temperature(read_chip=True)
                if ( data is not 0.0 ) and ( data < 100 ):  # First reading is sometimes Zero or Low / Sometimes crazy high
                    #print(f'Thermocouple Read: {data:.2f} C')
                    readings.append(data)
                #else:
                    #print(f'Thermocouple Read: {data:.2f} C ... ignoring reading')
                attempts -= 1
                sleep_ms(100)
            if len(readings) > 2:
                readings.remove(max(readings))
                readings.remove(min(readings))
                self.tempC = sum(readings)/len(readings) + self.adjustment
                self.tempF = (self.tempC * 9.0/5.0) + 32
                #print(f'Water Temp Avg:    {self.tempC:.2f} C')
                #print(f'Water Temp Avg:    {self.tempF:.2f} F')
            else:
                return None
        finally:
            self.spi.deinit()
            self.cs(1)  # Deselect Shared SPI Peripheral
