###################################
# Built-in Modules: help('modules')
###################################
import framebuf


###################################
# 3rd-Party Modules on Github
###################################
from writer_peterhinch import Writer
# Source: wget -O writer_peterhinch.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/writer.py


###################################
# My Custom Modules on Github
###################################
import GothamBlack_54_Numbers
import GothamBlack_25
from EPD_2in13_V3 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_V3_Portrait
#from EPD_2in13_B_V4 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_B_V4


###################################
# Waveshare Display Differences
###################################
epd = EPD_2in13_V3_Portrait()
#epd = EPD_2in13_B_V4()
if epd.__module__ is 'EPD_2in13_V3':
    epd.Clear()
    def FILL():
        epd.fill(0xff)  # Fill buffer with white space
    def DISPLAY():
        print('Updating Display...')
        epd.display(epd.buffer)
elif epd.__module__ is 'EPD_2in13_B_V4':
    epd.Clear(0xff,0xff)
    def FILL():
        epd.imageblack.fill(0xff)
        epd.imagered.fill(0xff)
    def DISPLAY():
        print('Updating Display...')
        epd.display()
else:
    print('Display Not Defined... Exiting')
    from sys import exit
    exit(1)


###################################
# Rounding like you learned in Math
###################################
def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)


###################################
# Load PBM Image to Display Buffer
###################################
def load_image(filename):  # inverted pbm files
    with open(filename, 'rb') as f:
        f.readline()
        f.readline()
        width, height = [int(v) for v in f.readline().split()]
        data = bytearray(f.read())
    return framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
# Source: https://blog.miguelgrinberg.com/post/micropython-and-the-internet-of-things-part-vi-working-with-a-screen


###################################
# Load Background Pool Image
###################################
pool_pbm = load_image('pool_graphic.pbm')


###################################
# Update Display Numbers
###################################
def update_number(temp=None, x=0):
    text = str(temp)
    if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
        import GothamBlack_46_Numbers
        # Source: wget -O Arial_50_Numbers.py https://raw.githubusercontent.com/peterhinch/micropython-nano-gui/master/gui/fonts/arial_50.py
        font_writer = Writer(epd, GothamBlack_46_Numbers, verbose=False)
    else:
        font_writer = Writer(epd, GothamBlack_54_Numbers, verbose=False)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    epd.rect(6,x,EPD_WIDTH-12,55,0xff,True)  # Draw White Rectangle before updated number is displayed
    font_writer.printstring(text, invert=True)


###################################
# Update Display Text
###################################
def update_text(text=None, x=0):
    font_writer = Writer(epd, GothamBlack_25, verbose=False)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    font_writer.printstring(text, invert=True)


###################################
# Main Display Update Function
###################################
def update(water=None, air=None, power=True, x=0):
    try:
        epd.cs_pin(0)  # Select Shared SPI Peripheral
        epd.spi.init(phase=0)  # Waveshare uses phase=0 and MAX31856 uses phase=1
        epd.init()
        #epd.TurnOnDisplay()
        #epd.delay_ms(2000)
        if not power:
            print('Power Disconnected...')
            FILL()  # Fill buffer with white space
            power_pbm = load_image('no_power_100px.pbm')
            epd.blit(power_pbm, (EPD_WIDTH - 100) // 2, (EPD_HEIGHT - 100) // 2)
            DISPLAY()
        else:
            FILL()  # Fill buffer with white space
            epd.blit(pool_pbm, 0, 0)
            if type(water) is str:  # Thermocouple Fault
                fault_pbm = load_image('fault_100px.pbm')
                epd.blit(fault_pbm, (EPD_WIDTH - 100) // 2, 150)
            elif water:
                update_number(temp=str(int(roundTraditional(water,0))), x=160)
                update_text(text='water', x=220)
            if air:
                update_number(temp=str(int(roundTraditional(air,0))), x=45)
                update_text(text='feels like', x=15)
            DISPLAY()
    finally:
        epd.delay_ms(2000)
        epd.sleep()
        epd.spi.deinit()
        epd.cs_pin(1)  # Deselect Shared SPI Peripheral