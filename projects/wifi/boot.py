'''
MicroPython: https://docs.micropython.org/en/latest/

Brandon Gant
Created: 2019-02-08
Updated: 2021-11-10

Source: https://github.com/micropython/micropython/tree/master/ports/esp32#configuring-the-wifi-and-using-the-board
Source: https://boneskull.com/micropython-on-esp32-part-1/
Source: https://docs.micropython.org/en/latest/library/network.WLAN.html

### Required Files:
boot.py
key_store.py

### Optional Files:
timezone.py
detect_filesystem.py
TinyPICO_RGB.py
client_id.py

### Software Installation on Linux:
mkdir ~/micropython-setup
cd ~/micropython-setup

python3 -m pip install pyvenv
python3 -m venv micropython-env
source micropython-env/bin/activate
python3 -m pip list | egrep -v "Package|----" | awk '{print $1}' | xargs -I {} python3 -m pip install --upgrade {}
python3 -m pip install esptool
python3 -m pip install mpremote
sudo usermod -aG `stat -c "%G" /dev/ttyUSB0` $USER  <-- May need to reboot PC 
mpremote connect /dev/ttyUSB0                       <-- test connection / Ctrl-] to exit

wget https://micropython.org/resources/firmware/tinypico-20210902-v1.17.bin
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 tinypico-20210902-v1.17.bin

git clone https://github.com/bgant/micropython-wifi
cd micropython-wifi/
mpremote cp key_store.py :
mpremote cp timezone.py :
mpremote cp TinyPICO_RGB.py :
mpremote cp boot.py :
mpremote  <-- to enter REPL
from machine import reset
reset()
<enter your Wifi SSID and Password and make sure it connects>
<if you made a mistake run import key_store and key_store.init() to change SSID and Password>
<Ctrl+] to exit REPL>
'''

print()
print('=' * 45)
print('boot.py: Press CTRL+C to enter REPL...')
print()
import utime
utime.sleep(2)  # A chance to hit Ctrl+C in REPL

from machine import reset, WDT
from sys import exit
from uos import uname

# Create exceptions (feedback) in cases where normal RAM allocation fails (e.g. interrupts)
from micropython import alloc_emergency_exception_buf
alloc_emergency_exception_buf(100)

wdt = WDT(timeout=300000)  # 5-minutes for boot.py to finish and move to main.py / wdt.feed() to reset timer

if 'TinyPICO' in uname().machine:
    try:
        import TinyPICO_RGB
        TinyPICO_RGB.off()
    except:
        print('TinyPICO_RGB.py module is not present')
        pass

def led(color):
    try:
        if color == 'red':
            TinyPICO_RGB.solid(255,0,0)
        elif color == 'blue':
            TinyPICO_RGB.solid(0,0,255)
        elif color == 'purple':
            TinyPICO_RGB.solid(255,0,255)
        else:
            TinyPICO_RGB.off()
    except:
        pass  # If TinyPICO_RGB.py is missing do nothing

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
def wlan_connect(ssid, password):
    import network
    from ubinascii import hexlify
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        print('       MAC: ', hexlify(wlan.config('mac'),':').decode())
        print(' WiFi SSID: ', ssid)
        led('purple')
        wlan.connect(ssid, password)
        start_wifi = utime.ticks_ms()
        while not wlan.isconnected():
            if utime.ticks_diff(utime.ticks_ms(), start_wifi) > 20000:  # 20 second timeout
                print('Wifi Timeout... Resetting Device')
                utime.sleep(2)
                reset()
    led('blue')
    print('        IP: ', wlan.ifconfig()[0])
    print('    Subnet: ', wlan.ifconfig()[1])
    print('   Gateway: ', wlan.ifconfig()[2])
    print('       DNS: ', wlan.ifconfig()[3])
    print()

# Set RTC using NTP
def ntp():
    import ntptime
    ntptime.host = key_store.get('ntp_host')
    print("NTP Server: ", ntptime.host)
    start_ntp = utime.ticks_ms()
    while utime.time() < 10000:  # Clock is not set with NTP if unixtime is less than 10000
        ntptime.settime()
        if utime.ticks_diff(utime.ticks_ms(), start_ntp) > 10000:  # 10 second timeout
                print('NTP Timeout... Resetting Device')
                reset()
    print('  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*utime.localtime()))
    print()
         
# Suppress ESP debug messages in the REPL
def no_debug():
    from esp import osdebug
    osdebug(None)

def mem_stats():
    from esp import flash_size
    from uos import statvfs
    import gc
    fs_stat = statvfs('/')
    fs_size = fs_stat[0] * fs_stat[2]
    fs_free = fs_stat[0] * fs_stat[3]
    print('Memory Information:')
    print('   RAM Size     {:5,}KB'.format(int((gc.mem_alloc() + gc.mem_free())/1024)))
    print()
    print('Flash Storage Information:')
    print('   Flash Size   {:5,}KB'.format(int(flash_size()/1024)))
    print('   User Space   {:5,}KB'.format(int(fs_size/1024)))
    print('   Free Space   {:5,}KB'.format(int(fs_free/1024)))

def filesystem():
    try:
        from detect_filesystem import check
        print('   File System ', check())
    except:
        print('detect_filesystem.py module is not present')
        pass

def list_files():
    from uos import listdir
    print()
    print("List of files on this device:")
    print('   %s' % '\n   '.join(map(str, sorted(listdir('/')))))
    print()

# Run selected functions at boot
try:
    no_debug()
    wlan_connect(ssid_name, ssid_pass)
    ntp()          # Only needed if using HTTPS or local timestamp data logging 
    mem_stats()
    #filesystem()  # Detect FAT or littlefs filesystem
    list_files()
except KeyboardInterrupt:
    wdt = WDT(timeout=86400000)  # Watchdog Timer cannot be disabled, so set to expire in 1 day
    led('off')
    exit()
except:
    print('ERROR... Resetting Device')
    led('red')
    utime.sleep(2)  # A chance to hit Ctrl+C in REPL
    reset()

wdt.feed() 
print('boot.py: end of script')
print('=' * 45)
print()
