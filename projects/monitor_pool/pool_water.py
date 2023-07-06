# Source: https://github.com/eliotb/micropython-max31856
from max31856_eliotb import Max31856
from machine import Pin, SPI

tc_type = 'K'  # K-Type Thermocouple
spi = SPI(1, baudrate=4000_000)   # Shared with Waveshare Display
cs = Pin(33, Pin.OUT)  # Assign its own chip select (CS) pin and start it high

# 'FAULT: tchigh+open+OV/UV+cjlow+tclow+cjhigh' error if you try to share the SPI bus
def water_temp():
    max31856 = Max31856(spi, cs, tc_type)
    fault, fault_string = max31856.faults(read_chip=True)  # read in all data from max31856 chip
    if fault:
        from machine import reset
        print(f'FAULT: {fault_string}... Resetting Device')
        from time import sleep
        sleep(5)
        reset()
        #return f'FAULT: {fault_string}'
    else:
        attempts = 5  # Try 5 readings max
        while attempts:
            thermoTempC = max31856.temperature(read_chip=True)
            attempts -= 1
            if not thermoTempC:
                break  # First reading is sometimes Zero / Exit loop if thermoTempC is not Zero
        thermoTempF = (thermoTempC * 9.0/5.0) + 32
        juncTempC = max31856.cold_junction()  # using data read at fault check
        juncTempF = (juncTempC * 9.0/5.0) + 32
        return thermoTempF

