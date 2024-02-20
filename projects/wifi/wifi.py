from machine import reset
from network import WLAN, STA_IF
from ubinascii import hexlify
import utime
import ntptime

try:
    import key_store
except:
    print('key_store.py module is not present')
    from sys import exit
    exit(1)

class WIFI:
    def __init__(self):
        self.wlan = WLAN(STA_IF)
        self.wlan.active(False)  # Disable on initialization
        
        # Load secrets from local key_store.db
        try:
            self.ssid_name = key_store.get('ssid_name')
            self.ssid_pass = key_store.get('ssid_pass')
            if not self.ssid_name or not self.ssid_pass:
                key_store.init()
        except:
            key_store.init()
            reset()
            
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
        print('  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
        print()
        