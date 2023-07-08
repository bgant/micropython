from machine import reset
import utime
import urequests
import network
import ntptime
from ubinascii import hexlify

# Load secrets from local key_store.db:
try:
    import key_store
except:
    print('key_store.py module is not present')
    from sys import exit
    exit(1)
try:
    ssid_name = key_store.get('ssid_name')
    ssid_pass = key_store.get('ssid_pass')
    if not ssid_name:
        key_store.init()
except:
    key_store.init()
    reset()

# Connect to WiFI:
wlan = network.WLAN(network.STA_IF)
def wlan_connect(ssid, password):
    print()
    print('       MAC: ', hexlify(wlan.config('mac'),':').decode())
    print(' WiFi SSID: ', ssid)
    while not wlan.isconnected():
        wlan.active(True)
        wlan.connect(ssid, password)
        start_wifi = utime.ticks_ms()
        while not wlan.isconnected():
            if utime.ticks_diff(utime.ticks_ms(), start_wifi) > 20000:  # 20 second connection timeout
                print('Wifi Timeout... Trying Again')
                wlan.active(False)
                utime.sleep(5)
                break
    print('        IP: ', wlan.ifconfig()[0])
    print('    Subnet: ', wlan.ifconfig()[1])
    print('   Gateway: ', wlan.ifconfig()[2])
    print('       DNS: ', wlan.ifconfig()[3])

# Set RTC using NTP:
ntptime.host = key_store.get('ntp_host')
def ntp():
    print("NTP Server: ", ntptime.host)
    attempts = 5  # Number of tries setting Time via NTP
    while attempts:
        try:
            ntptime.settime()
        except:
            pass
        attempts -= 1
        if utime.time() > 10000:  # Clock is not set with NTP unless unixtime is greater than 10000
            break
        utime.sleep(2)
    print('  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
    print()

# Download Air Temperature:
JSON_URL = 'https://api.openweathermap.org/data/2.5/weather?lat=' + key_store.get('lat') + '&lon=' + key_store.get('lon') + '&units=imperial&appid=' + key_store.get('appid')
download_hours = [h % 24 for h in range(13,28)]  # Between 8CST/13CST and 23CST/4UTC
def download_weather():
    if utime.localtime()[3] in download_hours:   # Run during certain hours to conserve API Calls
        try:
            response = urequests.get(JSON_URL)
            json_data = response.json()
            #print(json_data)
            air_temp = json_data['main']['feels_like']  # ['feels_like'] or ['temp']
            print(f'Air Feels Like:    {air_temp} F')
            return air_temp
        except:
            return None
    else:
        print(f'Skip Night-time Air Reading to conserve API calls...')
        return None

# Start Wifi and NTP on module import
wlan_connect(ssid_name,ssid_pass)
ntp()

# pool_wifi.wlan_connect(pool_wifi.ssid_name,pool_wifi.ssid_pass)
# pool_wifi.ntp()
# pool_wifi.wlan.active()
# pool_wifi.wlan.isconnected()
