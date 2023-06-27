# Source: https://github.com/eliotb/micropython-max31856
from max31856_eliotb import Max31856
from machine import Pin, SPI

tc_type = 'K'  # K-Type Thermocouple
spi = SPI(1)
cs = Pin(33, Pin.OUT)  # Assign chip select (CS) pin and start it high
max31856 = Max31856(spi, cs, tc_type)

def water_temp():
    fault, fault_string = max31856.faults(read_chip=True)  # read in all data from max31856 chip
    if fault:
        Return print(f"Fault: {fault_string}")
    else:
        thermoTempC = max31856.temperature()  # using data read at fault check
        thermoTempF = (thermoTempC * 9.0/5.0) + 32
        juncTempC = max31856.cold_junction()  # using data read at fault check
        juncTempF = (juncTempC * 9.0/5.0) + 32
        return thermoTempF

