import pool_water

from EPD_2in13_V3 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_V3_Portrait 
import GothamBlack_54_Numbers
import GothamBlack_25
import framebuf
from writer_peterhinch import Writer

epd = EPD_2in13_V3_Portrait()
epd.Clear()
epd.fill(0xff)  # Fill buffer with white space

# Source: https://blog.miguelgrinberg.com/post/micropython-and-the-internet-of-things-part-vi-working-with-a-screen
def load_image(filename):  # inverted pbm files
    with open(filename, 'rb') as f:
        f.readline()
        f.readline()
        width, height = [int(v) for v in f.readline().split()]
        data = bytearray(f.read())
    return framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

# Load Background Image into Buffer
pool_pbm = load_image('pool_graphic.pbm')
epd.blit(pool_pbm, 0, 0)

# Load 'water' text into Buffer
text = 'water'
font_writer = Writer(epd, GothamBlack_25)
textlen = font_writer.stringlen(text)
Writer.set_textpos(epd, 220, (EPD_WIDTH - textlen) // 2)
font_writer.printstring(text, invert=True)

# Function to update Temperature Numbers
def update_temp(temp=None, x=0):
    text = str(temp)
    if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
        import Arial_50_Numbers
        font_writer = Writer(epd, Arial_50_Numbers)
    else:
        font_writer = Writer(epd, GothamBlack_54_Numbers)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    epd.rect(5,x,EPD_WIDTH-textlen,55,0xff,True)    # Draw White Rectangle before updated number is displayed
    font_writer.printstring(text, invert=True)
    epd.display(epd.buffer)

epd.init()
update_temp(temp=str(int(pool_water.water_temp())), x=160)
epd.delay_ms(2000)
epd.sleep()
