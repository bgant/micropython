###################################
# Built-in Modules: help('modules')
###################################
from machine import Pin, SPI
from time import sleep


###################################
# 3rd-Party Modules on Github
###################################
from max31856_eliotb import Max31856
# Source: wget -O max31856_eliotb.py https://raw.githubusercontent.com/eliotb/micropython-max31856/master/max31856.py


###################################
# Max31856 Settings
###################################
tc_type = 'K'  # K-Type Thermocouple
spi = SPI(1)   # Shared settings with Waveshare Display
cs = Pin(33, Pin.OUT)  # Assign its own chip select (CS) pin and start it high
max31856 = Max31856(spi, cs, tc_type)  # 'FAULT: tchigh+open+OV/UV+cjlow+tclow+cjhigh' error if you try to share the SPI bus

###################################
# Read Thermocouple Temperature
###################################
def temp():
    try:
        cs(0)  # Select Shared SPI Peripheral
        spi.init(phase=1)  # Waveshare uses phase=0 and MAX31856 uses phase=1
        fault, fault_string = max31856.faults(read_chip=True)  # read in all data from max31856 chip
        if fault:
            print(f'THERMOCOUPLE FAULT: {fault_string}')
            return fault_string  # Only fix found so far is to cut power completely
        else:
            attempts = 10  # Number of tries
            while attempts:
                thermoTempC = max31856.temperature(read_chip=True)
                print(f'Thermocouple Read: {thermoTempC} C')
                if ( int(thermoTempC) is not 0 ) and ( int(thermoTempC) < 212 ):  # First reading is sometimes Zero / Sometimes crazy high
                    break
                attempts -= 1
                sleep(2)
            thermoTempF = (thermoTempC * 9.0/5.0) + 32
            print(f'Water Temp:        {thermoTempF} F')
            return thermoTempF
    finally:
        spi.deinit()
        cs(1)  # Deselect Shared SPI Peripheral
