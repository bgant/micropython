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
import network
from ubinascii import hexlify
import utime
import ntptime
from sys import exit, implementation

try:
    f = open('key_store.py','r')
    f.close()
    from key_store import KEY_STORE
except OSError:
    print('key_store.py is required to use this module')    
    exit()

class WIFI:
    def __init__(self):
        self.timeout_reset = False
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)  # Disable on initialization
        
        # Load secrets from local key_store.db
        key_store = KEY_STORE()
        if key_store.get('ssid_name') and key_store.get('ssid_pass'):
            self.ssid_name = key_store.get('ssid_name')
            self.ssid_pass = key_store.get('ssid_pass')
        else:  # key_store values are empty
            self.ssid_name = input('Enter WiFi SSID - ')
            self.ssid_pass = input('Enter WiFi password - ')
            key_store.set('ssid_name',self.ssid_name)
            key_store.set('ssid_pass',self.ssid_pass)
        if key_store.get('ntp_host'):
            ntptime.host = key_store.get('ntp_host')
        key_store.db.close()
        
        self.mac = ''
        self.ip = ''
        self.subnet = ''
        self.gateway = ''
        self.dns = ''
 
    def active(self):
        return self.wlan.active()
    
    def isconnected(self):
        return self.wlan.isconnected()
      
    def connect(self,need_ntp=False):
        if self.wlan.isconnected():
            return 'Wifi is already connected'
        else:
            self.wlan.active(False)
            utime.sleep_ms(500)
            self.wlan.active(True)
            utime.sleep_ms(500)
            
            self.start_wifi = utime.ticks_ms()
            self.wlan.config(reconnects=5)
            if 'TinyS3' in implementation[2]:
                self.wlan.config(pm=self.wlan.PM_NONE)
                self.wlan.config(txpower=5)  # values between 2 and 21 are valid
            
            self.mac = hexlify(self.wlan.config('mac'),':').decode()
            print('')
            print('       MAC: ', self.mac)
            print(' Wifi SSID: ', self.ssid_name)
            self.wlan.connect(self.ssid_name, self.ssid_pass)
            
            #while not self.wlan.isconnected():
            while not self.timeout_check() and (self.wlan.status() != network.STAT_GOT_IP):
                print('.', end='')
                utime.sleep_ms(200)
            #self.status()
                    
            print()      
            self.ip      = self.wlan.ifconfig()[0]
            self.subnet  = self.wlan.ifconfig()[1]
            self.gateway = self.wlan.ifconfig()[2]
            self.dns     = self.wlan.ifconfig()[3]
            print('        IP: ', self.ip)
            print('    Subnet: ', self.subnet)
            print('   Gateway: ', self.gateway)
            print('       DNS: ', self.dns)
            print()
            if need_ntp:
                self.ntp()
        
    def status(self):
        while self.wlan.status() != network.STAT_GOT_IP:
            print(' Wifi idle .', end='')
            while self.wlan.status() == network.STAT_IDLE:
                self.pause(10) 
            print(' WiFi connecting .', end='')
            while self.wlan.status() == network.STAT_CONNECTING:
                self.pause(10)
            print(' Wifi Security .', end='')
            while '20' in str(self.wlan.status()):  # 20x WRONG_PASSWORD, NO_AP_FOUND, BEACON_TIMEOUT, etc.
                self.pause(10)
            print(' ')
            utime.sleep(10)
            
    def pause(self,pause_ms=10):
        print('.', end='')
        utime.sleep(pause_ms)
        self.timeout_check()
    
    def timeout_check(self,timeout_seconds=25):
        if utime.ticks_diff(utime.ticks_ms(), self.start_wifi) > (timeout_seconds*1000):  # Wifi timeout in milliseconds
            if self.timeout_reset:
                print(' Wifi Timeout... Resetting Device')
                utime.sleep(1)
                reset()
            else:
                return True
        else:
            return False

    def ntp(self):
        print(f'NTP Server:  {ntptime.host} ', end='')
        try:
            ntptime.settime()
            utime.sleep_ms(1000)
        except:
            pass
        start_ntp = utime.ticks_ms()
        while utime.time() < 10000:  # Clock is not set with NTP if unixtime is less than 10000
            print('.', end='')
            try:
                ntptime.settime()  # If time is not UTC then Thonny is setting device time
            except:
                pass
            if utime.ticks_diff(utime.ticks_ms(), start_ntp) > 15000:  # 15 second timeout
                print('Timeout... Resetting Device')
                reset()
            utime.sleep_ms(1000)
        print()
        print('  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
        print()

'''
    200: BEACON_TIMEOUT
    201: NO_AP_FOUND
    202: WRONG_PASSWORD
    203: ASSOC_FAIL
    204: HANDSHAKE_TIMEOUT
    1000: IDLE
    1001: CONNECTING
    1010: GOT_IP
'''

'''
            if self.wlan.status() == network.STAT_NO_AP_FOUND:
                print (f' STAT_NO_AP_FOUND:', self.wlan.status())
            elif self.wlan.status() == network.STAT_BEACON_TIMEOUT:
                print (f' STAT_BEACON_TIMEOUT', self.wlan.status())
            elif self.wlan.status() == network.STAT_ASSOC_FAIL:
                print (f' STAT_ASSOC_FAIL', self.wlan.status())
            elif self.wlan.status() == network.STAT_HANDSHAKE_TIMEOUT:
                print (f' STAT_HANDSHAKE_TIMEOUT', self.wlan.status())
            elif self.wlan.status() == network.STAT_IDLE:
                pass
            elif self.wlan.status() == network.STAT_CONNECTING:
                pass
            elif self.wlan.status() == network.STAT_GOT_IP:
                pass
            #else:
            #    print(f'Unknown status:', self.wlan.status())
            print()
'''            

'''
            #start_wifi = utime.ticks_ms()
            #while not self.wlan.isconnected():
            #    if utime.ticks_diff(utime.ticks_ms(), start_wifi) > 20000:  # 20 second timeout
            #        print('Wifi Timeout... Resetting Device')
            #        utime.sleep(2)
            #        reset()
'''
