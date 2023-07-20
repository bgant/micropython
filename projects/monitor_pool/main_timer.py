''''
Brandon Gant
Created: 2023-05-06
Updated: 2023-05-08

Parts List:
    * Unexpected Maker TinyS3 (ESP32-S3 Board)
      https://www.amazon.com/dp/B09X259SDP

    * Waveshare 2.13in E-Ink Display HAT
      https://www.amazon.com/dp/B07P9T64BK (Pico_ePaper-2.13_V3.py   Black/White)
      https://www.amazon.com/dp/B07Q22WDB9 (Pico_ePaper-2.13-B_V4.py Black/White/Red)

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
  
Download Files to Upload to Micropython Device:
    wget -O EPD_2in13_V3.py https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python/Pico_ePaper-2.13-V3.py
    wget -O EPD_2in13_B_V4.py https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python/Pico_ePaper-2.13-B_V4.py
    wget -O writer_peterhinch.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/writer.py
    wget -O Arial_50_Numbers.py https://raw.githubusercontent.com/peterhinch/micropython-nano-gui/master/gui/fonts/arial_50.py
    wget -O max31856_eliotb.py https://raw.githubusercontent.com/eliotb/micropython-max31856/master/max31856.py

Edit EPD_2in13_B_V4.py Module to work with SPI:
    RST_PIN         = 21
    DC_PIN          = 22
    CS_PIN          = 5
    BUSY_PIN        = 32

Edit EPD_2in13_B_V4.py Module to work with SPI and Writer.py:
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
    python3 font_to_py.py GothamBlack.ttf 25 -x -c 1234567890wateri GothamBlack_25.py
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
from time import sleep, localtime
print('main.py: Press CTRL+C to enter REPL...')  # Time to enter REPL on power up
sleep(5)
from machine import reset, WDT, Timer, Pin
wdt = WDT(timeout=780000)  # Set 13-minute Hardware Watchdog Timer
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
vbus       = Pin(9, Pin.IN)  # Detect 5V Present


###################################
# Main Loop Function
###################################
def main(timer_main):
    global water_last
    global air_last
    global water_now
    global air_now
    
    # Collect Data:
    power_now = bool(vbus())       # Detect 5V Present
    if not power_now:
        pool_display.update(power=power_now)
    cpu_now   = raw_temperature()  # Reading in Fahrenheit / ESP32 Max Temp 125C/257F
    water_now = pool_thermocouple.temp()
    if pool_wifi.wlan.isconnected():
        gc.collect()
        air_now   = pool_wifi.download_weather()
    else:
        print('Wifi Not Connected... Reconnecting...')
        pool_wifi.wlan_connect(pool_wifi.ssid_name,pool_wifi.ssid_pass)
        gc.collect()
        air_now   = pool_wifi.download_weather()
    
    # Send Data to InfluxDB Server:
    try:
        pool_wifi.send_to_influxdb(water=water_now,cpu=cpu_now)
    except Exception as e:
        print(f'ERROR: Failed to connect to InfluxDB server: {e}')
        pass
    
    # Update Display:
    water_temp = int(roundTraditional(water_now,0)) if type(water_now) is float else water_now  # str or None
    air_temp   = int(roundTraditional(air_now,0))   if type(air_now)   is float else air_now    # None
    if (water_temp is water_last) and (air_temp is air_last):
        print('No Temperature Changes... Skipping Display Update...')
    else:
        pool_display.update(water=water_now, air=air_now)
    #print(f'Memory Free:   {int(gc.mem_free()/1024)}KB')
    print('='*45)
    
    # End of loop cleanup:
    water_last = water_now if not type(water_now) is float else int(roundTraditional(water_now,0))
    air_last = None if air_now is None else int(roundTraditional(air_now,0))
    wdt.feed()


###################################
# Timers to retain access to REPL
###################################

# Run the main loop through Timer:
timer_main = Timer(0)
main(timer_main) # Initial Run on Boot
timer_main.init(period=600000, mode=Timer.PERIODIC, callback=main)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

# Reset Every 12 hours to Clear Screen:
def reset_device(timer_reset):
    print('Resetting Device to Clear Screen...')
    reset()
timer_reset = Timer(1)
timer_reset.init(period=43200000, mode=Timer.PERIODIC, callback=reset_device)

# List of variables: dir()
# List of modules: help('modules')
# Time Commands: ntp()  time.localtime()  ntptime.settime()
