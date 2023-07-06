

from machine import reset
import utime

# Load secrets from local key_store.db
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

# Connect to WiFI
import network
wlan = network.WLAN(network.STA_IF)
def wlan_connect(ssid, password):
    from ubinascii import hexlify
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        print('       MAC: ', hexlify(wlan.config('mac'),':').decode())
        print(' WiFi SSID: ', ssid)
        wlan.connect(ssid, password)
        start_wifi = utime.ticks_ms()
        while not wlan.isconnected():
            if utime.ticks_diff(utime.ticks_ms(), start_wifi) > 20000:  # 20 second timeout
                print('Wifi Timeout... Resetting Device')
                utime.sleep(2)
                reset()
    print('        IP: ', wlan.ifconfig()[0])
    print('    Subnet: ', wlan.ifconfig()[1])
    print('   Gateway: ', wlan.ifconfig()[2])
    print('       DNS: ', wlan.ifconfig()[3])

# Set RTC using NTP
def ntp():
    import ntptime
    ntptime.host = key_store.get('ntp_host')
    print("NTP Server: ", ntptime.host)
    start_ntp = utime.ticks_ms()
    ntptime.settime()
    while utime.time() < 10000:  # Clock is not set with NTP if unixtime is less than 10000
        ntptime.settime()
        if utime.ticks_diff(utime.ticks_ms(), start_ntp) > 10000:  # 10 second timeout
                print('NTP Timeout... Resetting Device')
                reset()
    print('  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
    print()


# pool_wifi.wlan_connect(pool_wifi.ssid_name,pool_wifi.ssid_pass)
# pool_wifi.ntp()
# pool_wifi.wlan.active()
# pool_wifi.wlan.isconnected()


# Usage in Main Loop:
# air_temp = pool_wifi(water_temp=water_now)  # Turn on Wifi, Send Water Temp to InfluxDB, Get Air Temp, Turn off Wifi

# try:
#     all the wifi stuff
# except:
#     return None  # If try fails return None and display doesn't show air temp


