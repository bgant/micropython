# Source: https://github.com/eliotb/micropython-max31856
from max31856_eliotb import Max31856
from machine import Pin, SPI
from time import sleep

tc_type = 'K'  # K-Type Thermocouple
spi = SPI(1, baudrate=4000_000)   # Shared with Waveshare Display
cs = Pin(33, Pin.OUT)  # Assign its own chip select (CS) pin and start it high

# 'FAULT: tchigh+open+OV/UV+cjlow+tclow+cjhigh' error if you try to share the SPI bus
def temp():
    max31856 = Max31856(spi, cs, tc_type)
    fault, fault_string = max31856.faults(read_chip=True)  # read in all data from max31856 chip
    if fault:
        print(f'THERMOCOUPLE FAULT: {fault_string}')
        return fault_string  # Only fix found so far is to cut power completely
    else:
        attempts = 10  # Number of tries
        while attempts:
            thermoTempC = max31856.temperature(read_chip=True)
            print(f'Thermocouple:   {thermoTempC} C')
            if ( int(thermoTempC) is not 0 ) and ( int(thermoTempC) < 212 ):  # First reading is sometimes Zero / Sometimes crazy high
                break
            attempts -= 1
            sleep(2)
        thermoTempF = (thermoTempC * 9.0/5.0) + 32
        print(f'Thermocouple:   {thermoTempF} F')
        return thermoTempF
