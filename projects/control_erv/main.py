# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer
from utime import localtime

# Load key_store/secrets
from key_store import KEY_STORE
secrets = KEY_STORE()

# Connect to Wifi and set Clock
from wifi import WIFI
wifi = WIFI()
wifi.connect()

# Import Project Specific Modules
from vttouchw import VTTOUCHW
from OpenWeatherMap import WEATHER
from AirNowAPI import AQI
from utime import localtime
from timezone import tz

main_interval = 300000   # Minutes between Timer loops

class PROJECT:
    def __init__(self):
        self.erv = VTTOUCHW()

    def night(self):
        '''
        Is it night right now?
        '''
        self.night_hours = [h % 24 for h in range(20,7+24)]  # 8PM to 7AM
        if localtime(tz())[3] in self.night_hours:
            print('OFF: Nighttime')
            return True
        else:
            print('OK:  Daytime')
            return False

    def outside_too_hot_or_cold(self):
        '''
        Is it too hot or cold outside right now?
        '''
        self.weather = WEATHER()
        self.response = self.weather.download('temp')
        if self.response:
            if (self.response < 32) or (self.response > 90):
                print(f'OFF: Too hot or cold at {self.response}F')
                return True
            else:
                print(f'OK:  Outside temperature is good at {self.response}F')
                return False
        else:
            print(f'ERROR: API Response is {self.response}')
            return False

    def epa_aqi_bad(self):
        '''
        Is the EPA Air Quality Index too high right now?
        '''
        self.PM = AQI('PM')
        if self.PM > 125:
            print(f'OFF: EPA Air Quality is too high at {PM}')
            return True
        else:
            print(f'OK:  EPA Air Quality is good at {PM}')
            return False

    def local_aqi_bad(self):
        '''
        Is the outside Air Quality device to high right now? (neighbors burning leaves?)
        '''
        print('OK:  Local AQI device not installed yet')
        return False
    
    def erv_control(self):
        '''
        Check everything and decide whether to turn ERV On or Off
        '''
        if self.night():
            self.standby()
        elif not self.outside_too_hot_or_cold() and not self.epa_aqi_bad() and not self.local_aqi_bad():
            print('OK:  Daytime checks Passed')
            self.smart()
        else:
            print('OFF: Daytime checks Failed')
            self.standby()

    def smart(self):
        if (self.erv.state == 'smart') and ('OK' in self.erv.status):
            print('ERV already in Smart mode')
        else:
            print('Setting ERV to Smart mode...')
            self.erv.smart()    # Turn ON ERV

    def standby(self):
        if (self.erv.state == 'standby') and ('OK' in self.erv.status):
            print('ERV already in Standby mode.')
        else:
            print('Setting ERV to Standby Mode...')
            self.erv.standby()  # Turn OFF ERV


project = PROJECT()
timer_main = Timer(0)

def timer_function(timer_main):
    project.erv_control()
    wdt.feed()

timer_function(timer_main)  # Initial Run on Boot
timer_main.init(period=main_interval, callback=timer_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

