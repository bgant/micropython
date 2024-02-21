from machine import reset, WDT, Timer
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer
from utime import localtime


from vttouchw import VTTOUCHW
from openweathermap import API
from timezone import tz

main_interval = 180000   # 5 Minutes between checks


class CHECK:
    def __init__(self):
        self.erv = VTTOUCHW()

    def night():
        '''
        Is it night right now?
        '''
        self.night_hours = [h % 24 for h in range(20,31)]  # 8PM to 7AM
        if localtime(tz())[3] in self.night_hours:
            return True
        else:
            return False

    def outside_too_hot_or_cold():
        '''
        Is it too hot or cold outside right now?
        '''
        self.temp = API()
        if 32 < int(self.temp.download('temp')) < 90:
            return True
        else:
            return False

    def epa_aqi_bad():
        '''
        Is the EPA Air Quality Index too high right now?
        '''
        return False

    def local_aqi_bad():
        '''
        Is the outside Air Quality device to high right now? (neighbors burning leaves?)
        '''
        return False
    
    def everything():
        '''
        Check everything and decide whether to turn ERV On or Off
        '''
        if not self.night() and not self.outside_too_hot_or_cold() and not self.epa_aqi_bad() and not self.local_aqi_bad():
            self.erv.smart()    # Turn ON ERV
        else:
            self.erv.standby()  # Turn OFF ERV 

check = CHECK()
timer_main = Timer(0)

def callfunction(timer_main):
    check.everything()

callback(timer_main)  # Initial Run on Boot
timer_main.init(period=main_interval,callback=callfunction)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

