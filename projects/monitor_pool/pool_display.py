import GothamBlack_54_Numbers
import GothamBlack_25
import framebuf
from writer_peterhinch import Writer

# Select Waveshare Display Type:
from EPD_2in13_V3 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_V3_Portrait
epd = EPD_2in13_V3_Portrait()
#from EPD_2in13_B_V4 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_B_V4
#epd = EPD_2in13_B_V4()

# Different Commands for Different Displays:
if epd.__module__ is 'EPD_2in13_V3':
    epd.Clear()
    epd.fill(0xff)  # Fill buffer with white space
    def DISPLAY():
        print('Updating Display...')
        epd.display(epd.buffer)
elif epd.__module__ is 'EPD_2in13_B_V4':
    epd.Clear(0xff,0xff)
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)
    def DISPLAY():
        print('Updating Display...')
        epd.display()
else:
    print('Display Not Defined... Exiting')
    from sys import exit
    exit(1)

# Rounding the way you expect in Math
def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)

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
DISPLAY()
epd.delay_ms(2000)
epd.sleep()

# Function to update display Temperature:
def update_number(temp=None, x=0):
    text = str(temp)
    if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
        import Arial_50_Numbers
        font_writer = Writer(epd, Arial_50_Numbers, verbose=False)
    else:
        font_writer = Writer(epd, GothamBlack_54_Numbers, verbose=False)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    epd.rect(6,x,EPD_WIDTH-12,55,0xff,True)  # Draw White Rectangle before updated number is displayed
    font_writer.printstring(text, invert=True)

# Function to load text into Buffer:
def update_text(text=None, x=0):
    font_writer = Writer(epd, GothamBlack_25, verbose=False)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    font_writer.printstring(text, invert=True)
 
# Main update display function:
def update(water=None, air=None, power=True, x=0):
    epd.init()
    if not power:
        print('Power Disconnected...')
        epd.fill(0xff)  # Fill buffer with white space
        power_pbm = load_image('no_power_100px.pbm')
        epd.blit(power_pbm, (EPD_WIDTH - 100) // 2, (EPD_HEIGHT - 100) // 2)
        DISPLAY()
        epd.delay_ms(2000)
        epd.sleep()
        from sys import exit
        exit(1)
    else:
        if type(water) is str:  # Thermocouple Fault
            fault_pbm = load_image('fault_100px.pbm')
            epd.blit(fault_pbm, (EPD_WIDTH - 100) // 2, 150)
        elif water:
            update_number(temp=str(int(roundTraditional(water,0))), x=160)
            update_text(text='water', x=220)
        if air:
            update_number(temp=str(int(roundTraditional(air,0))), x=30)
            update_text(text='air', x=90)
        DISPLAY()
        epd.delay_ms(2000)
        epd.sleep()
