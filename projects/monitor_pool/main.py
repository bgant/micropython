''''
Brandon Gant
Created: 2023-05-06
Updated: 2023-08-01

Parts List:
    * Unexpected Maker TinyS3 (ESP32-S3 Board)
      https://www.amazon.com/dp/B09X259SDP

    * Waveshare 2.13in E-Ink Display HAT
      https://www.amazon.com/dp/B07P9T64BK (Pico_ePaper-2.13_V3.py   Black/White)

    * Adafruit Universal Thermocouple Amplifier MAX31856 Breakout
      https://www.adafruit.com/product/3263
      https://www.amazon.com/dp/B01LZBBI7D

    * Waterproof Stainless Steel K-Type Thermocouple
      https://www.amazon.com/dp/B07PNTDFGJ

    * qBoxMini DIY IOT Enclosure Kit
      https://www.amazon.com/dp/B088CRR7KS

    * M2.5 Hex Brass Standoff Assortment Kit
      https://www.amazon.com/product/B075K3QBMX

TinyS3 to Waveshare Pinout:
    ESP32          Waveshare
    SCK      <-->  CLK
    MO       <-->  DIN
    SS       <-->  CS
    IO32     <-->  BUSY
    IO21     <-->  RST
    IO22     <-->  DC
  
Files to Upload to Micropython Device:
    wget -O waveshare_2in13_V3.py https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python/Pico_ePaper-2.13-V3.py
    wget -O peterhinch_writer.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/writer.py
    wget -O eliotb_max31856.py https://raw.githubusercontent.com/eliotb/micropython-max31856/master/max31856.py
    wget -O client_id.py https://raw.githubusercontent.com/bgant/micropython/main/modules/client_id.py
    wget -O key_store.py https://raw.githubusercontent.com/bgant/micropython/main/modules/key_store.py
    wget -O TinyPICO_RGB.py https://raw.githubusercontent.com/bgant/micropython/main/modules/TinyPICO_RGB.py
    wget -O GothamBlack_25.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_25.py
    wget -O GothamBlack_46_Numbers.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_46_Numbers.py
    wget -O GothamBlack_54_Numbers.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_54_Numbers.py
    wget -O graphic_pool_122px.pbm https://github.com/bgant/micropython/raw/main/projects/monitor_pool/graphic_pool_122px.pbm
    wget -O graphic_no_power_100px.pbm https://github.com/bgant/micropython/raw/main/projects/monitor_pool/graphic_no_power_100px.pbm
    wget -O pool_thermocouple.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/pool_thermocouple.py
    wget -O pool_display.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/pool_display.py
    wget -O pool_wifi.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/pool_wifi.py
    wget -O main.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/main.py

Edit waveshare_2in13_V3.py Module to work with SPI:
    RST_PIN         = 21
    DC_PIN          = 22
    CS_PIN          = 5
    BUSY_PIN        = 32

Edit waveshare_2in13_B_V4.py Module to work with SPI and Writer.py:
  Source: https://www.instructables.com/Waveshare-E-paper-Display-With-Raspberry-Pi-Pico-M/
    RST_PIN         = 21
    DC_PIN          = 22
    CS_PIN          = 5
    BUSY_PIN        = 32
    
  - class EPD_2in13_B_V4:
  + class EPD_2in13_B_V4(framebuf.FrameBuffer):
  
    self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
  + super().__init__(self.buffer_balck, self.width, self.height, framebuf.MONO_HLSB)
    self.init()

Create Font Subsets to Upload to Micropython Device:
    wget https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/font_to_py.py
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip list
    python3 -m pip install freetype-py
    python3 font_to_py.py GothamBlack.ttf 25 -x -c 'airwaterfeels like' GothamBlack_25.py
    python3 font_to_py.py GothamBlack.ttf 46 -x -c 1234567890 GothamBlack_46_Numbers.py
    python3 font_to_py.py GothamBlack.ttf 54 -x -c 1234567890 GothamBlack_54_Numbers.py

Create No Power and Fault Images:
Source: https://learn.adafruit.com/preparing-graphics-for-e-ink-displays/command-line
    wget -O eink-2color.png https://cdn-learn.adafruit.com/assets/assets/000/079/735/medium800/eink___epaper_eink-2color.png
    <search and download image online>
    <Use Gimp to crop and fill black and white colors>
    convert no-power.jpg -negate -dither FloydSteinberg -define dither:diffusion-amount=100% -remap eink-2color.png PBM:no-power-large.pbm
    <Gimp --> Image --> Scale Image... to 100 pixels wide>

Secrets Storage on Device using key_store.py:
    key_store.set('ssid','')
    key_store.set('password','')
    key_store.set('lat','')
    key_store.set('lon','')
    key_store.set('appid','<from https://api.openweathermap.org>')
    key_store.set('server','')
    key_store.set('port','')  # 8086 or 443
    key_store.set('database','')
    key_store.set('measurement','')
    key_store.set('jwt','<from https://jwt.io/#debugger-io>')
    key_store.set('display_type','')

JSON Web Token (jwt)
    If you enabled authentication in InfluxDB you need
    to create a JSON Web Token to write to a database:

    https://www.unixtimestamp.com/index.php
        Create a future Unix Timestamp expiration   

    https://jwt.io/#debugger-io
        HEADER
            {
              "alg": "HS256",
              "typ": "JWT"
             }
        PAYLOAD
            {
              "username": "<InfluxDB username with WRITE to DATABASE>",
              "exp": <Unix Timestamp expiration>
            }
        VERIFY SIGNATURE
            HMACSHA256(
              base64UrlEncode(header) + "." +
              base64UrlEncode(payload),
              <shared secret phrase set in InfluxDB>
            )
'''

###################################
# Built-in Modules: help('modules')
###################################
from time import sleep, localtime, ticks_ms, ticks_diff
from machine import reset, WDT, Timer, Pin, lightsleep
print('main.py: Press CTRL+C to enter REPL...')  # Time to enter REPL on power up
sleep(5)

uptime = ticks_ms()
main_interval = 450000     # 7.5 Minute temperature readings
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer
from esp32 import raw_temperature
from tinypico import set_dotstar_power
set_dotstar_power(False)


###################################
# My Custom Modules on Github
###################################
import pool_display
import pool_wifi
import pool_thermocouple
from client_id import client_id


###################################
# Rounding like you learned in Math
###################################
def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)


###################################
# Global Values to Track
###################################
water_now  = None
air_now    = None
water_last = None
air_last   = None
power_last = True
vbus = Pin(9, Pin.IN)
state = 'lightsleep'  # lightsleep or timer (for debugging)


###################################
# Main Loop Function
###################################
def main(timer_main):
    # Set Global Variables
    global water_last
    global air_last
    global water_now
    global air_now
    global power_last
    
    # Display no_power_100px.pbm if running on battery
    if not vbus():
        import TinyPICO_RGB as led
        led.blink(255,0,0)
        if power_last:
            pool_wifi.wlan.active(False)
            pool_display.update(power=False)
            sleep(10)
            power_last = False
        wdt.feed()
        lightsleep(30000)
        return None
        
    # Reset and Clear Screen occasionally
    if ticks_diff(ticks_ms(), uptime) > 43200000:  # 12 hours
        reset()
    
    # Reconnect to Wifi
    wifi_reconnects = 0
    while wifi_reconnects <= 5:
        if not pool_wifi.wlan.isconnected():
            pool_wifi.wlan.active(True)
            print('Reconnecting to Wifi...')
            pool_wifi.wlan_connect(pool_wifi.ssid_name,pool_wifi.ssid_pass)
        wifi_reconnects += 1
    if pool_wifi.wlan.isconnected():
        pool_wifi.ntp()

    # Collect Data:
    cpu_now   = raw_temperature()  # Reading in Fahrenheit / ESP32 Max Temp 125C/257F
    water_now = pool_thermocouple.temp()
    gc.collect()
    if pool_wifi.wlan.isconnected():
        air_now = pool_wifi.download_weather()
    else:
        air_now = 'no wifi'
    
    # Send Data to InfluxDB Server:
    try:
        if pool_wifi.wlan.isconnected():
            pool_wifi.send_to_influxdb(water=water_now,cpu=cpu_now)
        else:
            print('No Wifi to send InfluxDB data...')
    except Exception as e:
        print(f'ERROR: Failed to connect to InfluxDB server: {e}')
        pass
    
    # Update Display:
    water_temp = int(roundTraditional(water_now,0)) if type(water_now) is float else water_now  # str or None
    air_temp   = int(roundTraditional(air_now,0))   if type(air_now)   is float else air_now    # str or None
    if (water_temp is water_last) and (air_temp is air_last):
        print('No Temperature Changes... Skipping Display Update...')
    else:
        pool_display.update(water=water_now, air=air_now)
    #print(f'Memory Free:   {int(gc.mem_free()/1024)}KB')
    print('='*45)
    
    # End of loop cleanup:
    water_last = water_now if not type(water_now) is float else int(roundTraditional(water_now,0))
    air_last   =   air_now if not type(air_now)   is float else int(roundTraditional(air_now,0))
    power_last = True
    wdt.feed()
    sleep(3)
    if state is 'lightsleep':
        print('Going to sleep now...')
        pool_wifi.wlan.active(False)  # Source: https://forum.micropython.org/viewtopic.php?t=10483
        sleep(2)
        lightsleep(main_interval)


###################################
# Run with timer or lightsleep
###################################
if state is 'timer':
    timer_main = Timer(0)
    main(timer_main) # Initial Run on Boot
    timer_main.init(period=main_interval, mode=Timer.PERIODIC, callback=main)
    # View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()
elif state is 'lightsleep':
    while True:
        main(None)
else:
    print(f'Unknown State: {state}')
    

# List of variables: dir()
# List of modules: help('modules')
# Time Commands: ntp()  time.localtime()  ntptime.settime()
