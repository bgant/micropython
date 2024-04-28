# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer
main_interval = 60         # Time in seconds between loops
state = 'loop'            # while 'loop' or 'timer'

# Load key_store/secrets
from key_store import KEY_STORE
key_store = KEY_STORE()

# Connect to Wifi and set Clock
from wifi import WIFI
wifi = WIFI()
wifi.connect()

# Import Project specific modules


class PROJECT:
    def __init__(self):
        pass

    def something(self):
        pass


project = PROJECT()

def timer_function(timer_main):
    project.something()
    wdt.feed()


###################################
# Run in timer or loop
###################################
if state is 'timer':
    print('main.py running in Timer')
    timer_main = Timer(0)
    timer_function(timer_main)  # Initial Run on Boot
    timer_main.init(period=main_interval*1000, callback=timer_function)
    # View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()
elif state is 'loop':
    print('main.py running in while True loop (Ctrl+C to REPL)')
    while True:
        timer_function(None)
        sleep_ms(main_interval*1000)
else:
    print(f'Unknown State: {state}')

