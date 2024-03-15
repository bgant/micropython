from machine import reset, WDT, Timer
wdt = WDT(timeout=60000)  # Set 1-minute Hardware Watchdog Timer
main_interval = 15        # Time in seconds between Timer loops

from key_store import KEY_STORE
key_store = KEY_STORE()

from wifi import WIFI
wifi = WIFI()
wifi.connect()

from DFRobot_MicroPython_A02YYUW import DFRobot_A02_Distance

class PROJECT:
    def __init__(self):
        self.ultrasonic = DFRobot_A02_Distance(rx=37)

    def control(self):
        values = []
        for i in range(10):
            values.append(self.ultrasonic.getDistance())
        values.sort()
        self.distance = int(sum(values[3:7])/len(values[3:7]))
        print(f'{self.distance}mm')
        self.send_to_influxdb(self.distance)
    
    def send_to_influxdb(self,distance=None):
        pass

project = PROJECT()
timer_main = Timer(0)

def timer_function(timer_main):
    project.control()
    wdt.feed()

timer_function(timer_main)  # Initial Run on Boot
timer_main.init(period=main_interval*1000, callback=timer_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

