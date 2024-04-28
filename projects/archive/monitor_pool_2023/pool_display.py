###################################
# Built-in Modules: help('modules')
###################################
import framebuf


###################################
# 3rd-Party Modules on Github
###################################
# wget -O peterhinch_writer.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/writer.py
from peterhinch_writer import Writer


###################################
# My Custom Modules on Github
###################################
# wget -O GothamBlack_54_Number.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_54_Numbers.py
import GothamBlack_54_Numbers
# wget -O GothamBlack_25.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_25.py
import GothamBlack_25
# wget -O key_store.py https://raw.githubusercontent.com/bgant/micropython/main/modules/key_store.py
import key_store


###################################
# Waveshare Display Differences
###################################
display_type = key_store.get('display_type')
print(f'E-Ink Display is {display_type}')
if display_type == 'EPD_2in13_V3':  # Waveshare 2.13" Black/White E-Ink (V3 Silver Sticker)
    # wget -O waveshare_2in13_V3.py https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python/Pico_ePaper-2.13_V3.py
    from waveshare_2in13_V3 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_V3_Portrait
    epd = EPD_2in13_V3_Portrait()
    epd.Clear()
    def FILL():
        epd.fill(0xff)  # Fill buffer with white space
    def DISPLAY():
        print('Updating Display...')
        epd.display(epd.buffer)
elif display_type == 'EPD_2in13_B_V4':  # Waveshare 2.13" Black/White/Red E-Ink (V4 Silver Sticker)
    # wget -O waveshare_2in13_B_V4.py https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/main/python/Pico_ePaper-2.13-B_V4.py
    from waveshare_2in13_B_V4 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_B_V4
    epd = EPD_2in13_B_V4()
    epd.Clear(0xff,0xff)
    def FILL():
        epd.imageblack.fill(0xff)
        epd.imagered.fill(0xff)
    def DISPLAY():
        print('Updating Display...')
        epd.display()
else:
    print('''key_store.get('display_type') not found... Exiting''')
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
# Update Display Numbers
###################################
def update_number(temp=None, x=0):
    text = str(temp)
    if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
        # wget -O GothamBlack_46_Number.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_46_Numbers.py
        import GothamBlack_46_Numbers
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
            epd.blit(load_image('graphic_no_power_100px.pbm'), (EPD_WIDTH - 100) // 2, (EPD_HEIGHT - 100) // 2)
            DISPLAY()
        else:
            FILL()  # Fill buffer with white space
            epd.blit(load_image('graphic_pool_122px.pbm'), 0, 0)
            # Display Water information:
            if not water or type(water) is str:  # None or Thermocouple Fault String
                epd.blit(load_image('graphic_fault_100px.pbm'), (EPD_WIDTH - 100) // 2, 150)
            elif water:
                update_number(temp=str(int(roundTraditional(water,0))), x=160)
                update_text(text='water', x=220)
            #Display Air information:
            if air is 'no wifi':
                epd.blit(load_image('graphic_no_wifi_100px.pbm'), (EPD_WIDTH - 100) // 2, 15)
            elif air:
                update_number(temp=str(int(roundTraditional(air,0))), x=45)
                update_text(text='feels like', x=15)
            DISPLAY()
    finally:
        epd.delay_ms(2000)
        epd.sleep()
        epd.spi.deinit()
        epd.cs_pin(1)  # Deselect Shared SPI Peripheral