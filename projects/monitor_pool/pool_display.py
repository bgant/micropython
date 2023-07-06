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

# Function to update display Temperature:
def update_number(temp=None, x=0):
    text = str(temp)
    if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
        import Arial_50_Numbers
        font_writer = Writer(epd, Arial_50_Numbers)
    else:
        font_writer = Writer(epd, GothamBlack_54_Numbers)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    epd.rect((EPD_WIDTH-textlen)//2,x,textlen,55,0xff,True)  # Draw White Rectangle before updated number is displayed
    font_writer.printstring(text, invert=True)

# Function to load text into Buffer:
def update_text(text=None, x=0):
    font_writer = Writer(epd, GothamBlack_25)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    font_writer.printstring(text, invert=True)
 
# Main update display function:
def update(water=None, air=None, power=True, x=0):
    epd.init()
    if not power:
        # Error: No Power
        epd.fill(0xff)  # Fill buffer with white space
        power_pbm = load_image('no_power_100px.pbm')
        epd.blit(power_pbm, (EPD_WIDTH - 100) // 2, (EPD_HEIGHT - 100) // 2)
    else:
        if water:
            update_number(temp=str(water), x=160)
            update_text(text='water', x=220)
        if air:
            update_number(temp=str(air), x=30)
            update_text(text='air', x=90)
    epd.display(epd.buffer)
    epd.delay_ms(2000)
    epd.sleep()

#epd.init()
#update_temp(temp=str(int(pool_water.water_temp())), x=160)
#epd.delay_ms(2000)
#epd.sleep()
