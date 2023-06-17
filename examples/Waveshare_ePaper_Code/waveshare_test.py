'''
# ESP32_Pico_Kit_v4.1 to Waveshare Pinout:
# Source: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/_images/esp32-pico-kit-v4-pinout.png

    ESP32          Waveshare
    HSPICLK  <-->  CLK
    HSPID    <-->  DIN     (SPID is MOSI / SPIQ is MISO)
    HSPICS0  <-->  CS
    GPIO05   <-->  BUSY
    GPIO10   <-->  RST
    GPIO09   <-->  DC
  
# Download Files to Upload to Micropython Device:
wget -O EPD_2in13_B_V4.py https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python/Pico_ePaper-2.13-B_V4.py
wget https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/writer.py
wget -O Arial_50_Numbers.py https://raw.githubusercontent.com/peterhinch/micropython-nano-gui/master/gui/fonts/arial_50.py

# Edit EPD_2in13_B_V4.py Module to work with SPI and Writer.py:
# Source: https://www.instructables.com/Waveshare-E-paper-Display-With-Raspberry-Pi-Pico-M/
    RST_PIN         = 10
    DC_PIN          = 9
    CS_PIN          = 15
    BUSY_PIN        = 5
    
  - class EPD_2in13_B_V4:
  + class EPD_2in13_B_V4(framebuf.FrameBuffer):
  
    self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
  + super().__init__(self.buffer_balck, self.width, self.height, framebuf.MONO_HLSB)
    self.init()

# Create Font Subsets to Upload to Micropython Device:
wget https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/font_to_py.py
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip list
python3 -m pip install freetype-py
python3 font_to_py.py GothamBlack-25.bdf 25 -x -c 1234567890wateri GothamBlack_25.py
python3 font_to_py.py GothamBlack-54.bdf 54 -x -c 1234567890 GothamBlack_54_Numbers.py

# Create No Power / No Wifi Images:
# Source: https://learn.adafruit.com/preparing-graphics-for-e-ink-displays/command-line
wget -O eink-2color.png https://cdn-learn.adafruit.com/assets/assets/000/079/735/medium800/eink___epaper_eink-2color.png
<search and download image online>
<Use Gimp to crop and fill colors>
convert no-power.jpg -negate -dither FloydSteinberg -define dither:diffusion-amount=100% -remap eink-2color.png PBM:no-power-large.pbm
<Use Gimp to resize pbm image>
'''

import GothamBlack_54_Numbers  # https://github.com/peterhinch/micropython-font-to-py
import GothamBlack_25
import framebuf  # https://docs.micropython.org/en/latest/library/framebuf.html
from writer import Writer  # https://github.com/peterhinch/micropython-font-to-py/tree/master/writer
from EPD_2in13_B_V4 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_B_V4  # https://github.com/waveshareteam/Pico_ePaper_Code/tree/main/python

epd = EPD_2in13_B_V4()
epd.imageblack.fill(0xff)
epd.imagered.fill(0xff)

def load_image(filename):  # inverted pbm files
    with open(filename, 'rb') as f:
        f.readline()
        f.readline()
        width, height = [int(v) for v in f.readline().split()]
        data = bytearray(f.read())
    return framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

# Load Background Image into Buffer
pool_pbm = load_image('pool.pbm')
epd.blit(pool_pbm, 0, 0)

# Load 'air' text into Buffer
text = 'air'
font_writer = Writer(epd, GothamBlack_25)
textlen = font_writer.stringlen(text)
Writer.set_textpos(epd, 90, (EPD_WIDTH - textlen) // 2)
font_writer.printstring(text, invert=True)

# Load 'water' text into Buffer
text = 'water'
font_writer = Writer(epd, GothamBlack_25)
textlen = font_writer.stringlen(text)
Writer.set_textpos(epd, 220, (EPD_WIDTH - textlen) // 2)
font_writer.printstring(text, invert=True)

# Function to update Temperature Numbers
def update_temp(temp=None, x=0):
    epd.rect(5,x,EPD_WIDTH-10,55,0xff,True) # Draw White Rectangle before updated number is displayed
    text = str(temp)
    if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
        import Arial_50_Numbers
        font_writer = Writer(epd, Arial_50_Numbers)
    else:
        font_writer = Writer(epd, GothamBlack_54_Numbers)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    font_writer.printstring(text, invert=True)

# Error No Power / No Wifi
wifi_pbm = load_image('no-power-100.pbm')
epd.blit(wifi_pbm, (EPD_WIDTH - 100) // 2, 10)

# Future For Loop to update temps
epd.init()   # Wake Waveshare from sleep
#update_temp(temp='74', x=30)
update_temp(temp='85', x=160)
epd.display()
epd.delay_ms(2000)
epd.sleep()  # Power down Waveshare when not in use
