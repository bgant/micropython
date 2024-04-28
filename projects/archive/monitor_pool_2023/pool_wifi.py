###################################
# Built-in Modules: help('modules')
###################################
from machine import reset
import utime
import urequests
import network
import ntptime
from ubinascii import hexlify


###################################
# My Custom Modules on Github
###################################
# wget -O client_id.py https://raw.githubusercontent.com/bgant/micropython/main/modules/client_id.py
from client_id import client_id


###################################
# Load secrets from key_store.db
###################################
# wget -O key_store.py https://raw.githubusercontent.com/bgant/micropython/main/modules/key_store.py
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


###################################
# Connect to Wifi
###################################
wlan = network.WLAN(network.STA_IF)
mac = hexlify(wlan.config('mac'),':').decode()
def wlan_connect(ssid, password):
    print()
    print(f'      WiFi: {ssid_name}')
    wlan.active(True)
    wlan.connect(ssid, password)
    start_wifi = utime.ticks_ms()
    while not wlan.isconnected():
        if utime.ticks_diff(utime.ticks_ms(), start_wifi) > 20000:  # 20 second connection timeout
            print('Wifi Timeout...')
            wlan.active(False)
            utime.sleep(5)
            break
    else:
        print(f'       MAC: {mac}')
        print(f'        IP: {wlan.ifconfig()[0]}')
        print(f'    Subnet: {wlan.ifconfig()[1]}')
        print(f'   Gateway: {wlan.ifconfig()[2]}')
        print(f'       DNS: {wlan.ifconfig()[3]}')


###################################
# Set Device Clock using NTP
###################################
ntptime.host = key_store.get('ntp_host')
def ntp():
    print(f'NTP Server: {ntptime.host}')
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
    print('  UTC Time: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
    print()


###################################
# Download Air Temperature
###################################
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


###################################
# Send Data to InfluxDB Function
###################################
server      = key_store.get('server')
port        = key_store.get('port')
database    = key_store.get('database')
measurement = key_store.get('measurement')
jwt         = key_store.get('jwt')
def send_to_influxdb(water=None,cpu=None):
    if '443' in port:
        url = f'https://{server}/influx/write?db={database}'
    else:
        url = f'http://{server}:{port}/write?db={database}'
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Authorization': ''
    }
    headers['Authorization'] = f'Bearer {jwt}'
    data = f'{measurement},device={client_id} waterF={water},cpuF={cpu}'
    response = urequests.post(url, headers=headers, data=data)
    if '204' in str(response.status_code):  # HTTP Status 204 (No Content) indicates server fulfilled request
        print(f'InfluxDB: {database} \t Measurement: {data} \t Status: {response.status_code} Success')
    else:
        print(f'InfluxDB: {database} \t Measurement: {data} \t Status: {response.status_code} Failed')

# pool_wifi.wlan_connect(pool_wifi.ssid_name,pool_wifi.ssid_pass)
# pool_wifi.ntp()
# pool_wifi.wlan.active()
# pool_wifi.wlan.isconnected()
