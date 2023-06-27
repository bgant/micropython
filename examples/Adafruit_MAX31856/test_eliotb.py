# Source: https://github.com/eliotb/micropython-max31856
from max31856_eliotb import Max31856
from machine import Pin, SPI
from time import sleep

tc_type = 'K'  # K-Type Thermocouple
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)  # Assign chip select (CS) pin and start it high
max31856 = Max31856(spi, cs, tc_type)

while True:
    fault, fault_string = max31856.faults(read_chip=True)  # read in all data from max31856 chip
    if fault:
        print(f"Fault: {fault_string}")
    else:
        thermoTempC = max31856.temperature()  # using data read at fault check
        thermoTempF = (thermoTempC * 9.0/5.0) + 32
        juncTempC = max31856.cold_junction()  # using data read at fault check
        juncTempF = (juncTempC * 9.0/5.0) + 32
        print(f"Thermocouple Temp: {thermoTempF:.1f}°F         Cold Junction Temp: {juncTempF:.1f}°F")
    sleep(3)