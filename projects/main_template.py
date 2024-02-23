# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer

# Load key_store/secrets
from key_store import KEY_STORE
secrets = KEY_STORE()

# Connect to Wifi and set Clock
from wifi import WIFI
wifi = WIFI()
wifi.connect()

# Import Project specific modules
from vttouchw import VTTOUCHW
from OpenWeatherMap import WEATHER
from AirNowAPI import AQI
from timezone import tz

main_interval = 300000   # Minutes between Timer loops

class PROJECT:
    def __init__(self):
        pass

    def something(self):
        pass


project = PROJECT()
timer_main = Timer(0)

def timer_function(timer_main):
    project.something()
    wdt.feed()

timer_function(timer_main)  # Initial Run on Boot
timer_main.init(period=main_interval, callback=timer_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

