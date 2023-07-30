###################################
# Built-in Modules: help('modules')
###################################
from machine import Pin, SPI
from time import sleep_ms


###################################
# 3rd-Party Modules on Github
###################################
from max31856_eliotb import Max31856
# Source: wget -O max31856_eliotb.py https://raw.githubusercontent.com/eliotb/micropython-max31856/master/max31856.py


###################################
# Max31856 Settings
###################################
tc_type = 'K'  # K-Type Thermocouple
spi = SPI(1)   # Shared SPI with Waveshare Display
cs = Pin(33, Pin.OUT)  # Assign its own chip select (CS) pin
max31856 = Max31856(spi, cs, tc_type)


###################################
# Read Thermocouple Temperature
###################################
def temp():
    try:
        cs(0)  # Select Shared SPI Peripheral
        spi.init(phase=1)  # Waveshare uses phase=0 and MAX31856 uses phase=1
        attempts = 13  # Number of tries
        print(f'Taking {attempts} temperature readings to average...')
        readings = []
        while attempts:
            thermoTempC = max31856.temperature(read_chip=True)
            print(f'Thermocouple Read: {thermoTempC} C')
            if ( int(thermoTempC) is not 0 ) and ( int(thermoTempC) < 100 ):  # First reading is sometimes Zero / Sometimes crazy high
                readings.append(thermoTempC)
            attempts -= 1
            sleep_ms(400)
        readings.remove(max(readings))
        readings.remove(min(readings))
        thermoTempC = sum(readings)/len(readings)
        thermoTempF = (thermoTempC * 9.0/5.0) + 32
        print(f'Water Temp:        {thermoTempF} F')
        return thermoTempF
    finally:
        spi.deinit()
        cs(1)  # Deselect Shared SPI Peripheral
