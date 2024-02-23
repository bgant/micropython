'''
Module import example:
  from wifi import WIFI
  mywifi = WIFI()
  mywifi.connect()
  mywifi.ntp()
  mywifi.isconnected()
  help(mywifi.wlan)
  print(mywifi.ip)
'''

from machine import reset
from network import WLAN, STA_IF
from ubinascii import hexlify
import utime
import ntptime
from sys import exit

try:
    f = open('key_store.py','r')
    f.close()
    from key_store import KEY_STORE
    key_store = KEY_STORE()
except OSError:
    print('key_store.py is required to use this module')    
    exit()

class WIFI:
    def __init__(self):
        self.wlan = WLAN(STA_IF)
        self.wlan.active(False)  # Disable on initialization
        
        # Load secrets from local key_store.db
        if key_store.get('ssid_name') and key_store.get('ssid_pass'):
            self.ssid_name = key_store.get('ssid_name')
            self.ssid_pass = key_store.get('ssid_pass')
        else:  # key_store values are empty
            self.ssid_name = input('Enter WiFi SSID - ')
            self.ssid_pass = input('Enter WiFi password - ')
            key_store.set('ssid_name',self.ssid_name)
            key_store.set('ssid_pass',self.ssid_pass)
            
        self.mac = ''
        self.ip = ''
        self.subnet = ''
        self.gateway = ''
        self.dns = ''
    
    def active(self):
        return self.wlan.active()
    
    def isconnected(self):
        return self.wlan.isconnected()
    
    def disconnect(self):
        self.wlan.active(False)
        return 'Wifi Off'
    
    def connect(self):
        if self.wlan.isconnected():
            return 'Wifi is already connected and working'
        else:
            self.wlan.active(False)
            self.wlan.active(True)
            
            self.mac = hexlify(self.wlan.config('mac'),':').decode()
            print('       MAC: ', self.mac)
            print(' WiFi SSID: ', self.ssid_name)
            try:
                self.wlan.connect(self.ssid_name, self.ssid_pass)
            except:
                pass
            self.start_wifi = utime.ticks_ms()
            while not self.wlan.isconnected():
                if utime.ticks_diff(utime.ticks_ms(), self.start_wifi) > 20000:  # 20 second timeout
                    print('Wifi Timeout... Resetting Device')
                    utime.sleep(2)
                    reset()
            self.ip      = self.wlan.ifconfig()[0]
            self.subnet  = self.wlan.ifconfig()[1]
            self.gateway = self.wlan.ifconfig()[2]
            self.dns     = self.wlan.ifconfig()[3]
            print('        IP: ', self.ip)
            print('    Subnet: ', self.subnet)
            print('   Gateway: ', self.gateway)
            print('       DNS: ', self.dns)
            print()
            self.ntp()
            return

    def ntp(self):
        #ntptime.host = key_store.get('ntp_host')
        print("NTP Server: ", ntptime.host)
        self.start_ntp = utime.ticks_ms()
        while utime.time() < 10000:  # Clock is not set with NTP if unixtime is less than 10000
            ntptime.settime()  # If time is not UTC then Thonny is setting device time
            if utime.ticks_diff(utime.ticks_ms(), self.start_ntp) > 10000:  # 10 second timeout
                print('NTP Timeout... Resetting Device')
                reset()
        else:
            ntptime.settime()
        print('  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
        print()
        
