###################################
# Built-in Modules: help('modules')
###################################
import framebuf


###################################
# 3rd-Party Modules on Github
###################################
# mpremote a0 mip install --target= github:peterhinch/micropython-font-to-py/writer/writer.py
from writer import Writer


###################################
# My Custom Modules on Github
###################################
# mpremote a0 mip install --target= github:bgant/micropython/modules/key_store.py
# mpremote a0 mip install --target= github:bgant/micropython/projects/monitor_pool_2024/GothamBlack_54_Numbers.py
# mpremote a0 mip install --target= github:bgant/micropython/projects/monitor_pool_2024/GothamBlack_25.py
import GothamBlack_54_Numbers
import GothamBlack_25
from key_store import KEY_STORE
key_store = KEY_STORE()

# Load secrets from local key_store.db
if key_store.get('display_type'):
    display_type = key_store.get('display_type')
else:  # key_store values are empty
    options = ['EPD_2in13_V3','EPD_2in13_B_V4']
    user_input = ''
    input_message = "Pick a Display option:\n"
    for index, item in enumerate(options):
        input_message += f'{index+1}) {item}\n'
    input_message += 'Your choice: '
    while user_input not in map(str, range(1, len(options) + 1)):
        user_input = input(input_message)
    choice = options[int(user_input) - 1]
    print(f'You picked: {choice}')
    key_store.set('display_type',choice)


class EPAPER:
    def __init__(self):
        '''Waveshare Display Differences'''
        self.display_type = key_store.get('display_type')
        print(f'E-Ink Display is {self.display_type}')
        if self.display_type == 'EPD_2in13_V3':  # Waveshare 2.13" Black/White E-Ink (V3 Silver Sticker)
            '''
mpremote a0 mip install --target= github:waveshareteam/Pico_ePaper_Code/python/Pico_ePaper-2.13_V3.py
mpremote a0 cp :Pico_ePaper-2.13_V3.py :Pico_ePaper_2in13_V3.py   # No '.' or '-' in micropython module names allowed
mpremote a0 rm :Pico_ePaper-2.13_V3.py

Edit Pico_ePaper_2in13_V3.py to work with SPI:

    def ReadBusy(self):
        print('busy')
        self.delay_ms(10)
-       while(self.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
+       while self.digital_read(self.busy_pin) == 1:      # 0: idle, 1: busy

from sys import implementation
if 'TinyPico' in implementation[2]:
    RST_PIN         = 21
    DC_PIN          = 22
    CS_PIN          = 5
    BUSY_PIN        = 32
elif 'TinyS3' in implementation[2]:
    RST_PIN         = 8
    DC_PIN          = 9
    CS_PIN          = 34
    BUSY_PIN        = 7
            '''
            from Pico_ePaper_2in13_V3 import EPD_2in13_V3_Portrait
            self.epd = EPD_2in13_V3_Portrait()
            self.epd.Clear()
            
        elif self.display_type == 'EPD_2in13_B_V4':  # Waveshare 2.13" Black/White/Red E-Ink (V4 Silver Sticker)
            '''
mpremote a0 mip install --target= github:waveshareteam/Pico_ePaper_Code/python/Pico_ePaper-2.13-B_V4.py
mpremote a0 cp :Pico_ePaper-2.13-B_V4.py :Pico_ePaper_2in13_B_V4.py
mpremote a0 rm :Pico_ePaper-2.13-B_V4.py  # No '.' or '-' in micropython module names allowed

Edit Pico_ePaper_2in13_B_V4.py to work with SPI and Writer.py:

from sys import implementation
if 'TinyPico' in implementation[2]:
    RST_PIN         = 21
    DC_PIN          = 22
    CS_PIN          = 5
    BUSY_PIN        = 32
elif 'TinyS3' in implementation[2]:
    RST_PIN         = 8
    DC_PIN          = 9
    CS_PIN          = 34
    BUSY_PIN        = 7

    def ReadBusy(self):
        print('busy')
-       while(self.digital_read(self.busy_pin) == 1): 
+       while self.digital_read(self.busy_pin) == 1:

- class EPD_2in13_B_V4_Portrait:
+ class EPD_2in13_B_V4_Portrait(framebuf.FrameBuffer):
  
  self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
+ super().__init__(self.buffer_balck, self.width, self.height, framebuf.MONO_HLSB)
  self.init()
            ''' 
            from Pico_ePaper_2in13_B_V4 import EPD_2in13_B_V4_Portrait
            self.epd = EPD_2in13_B_V4_Portrait()
            self.epd.Clear(0xff,0xff)
        else:
            print(f'Display Type {self.display_type} not found... Exiting')
            from sys import exit
            exit(1)

    def fill(self):  # Device specific fill
        if self.display_type == 'EPD_2in13_V3':
            self.epd.fill(0xff)  # Fill buffer with white space
        elif self.display_type == 'EPD_2in13_B_V4':
            self.epd.imageblack.fill(0xff)
            self.epd.imagered.fill(0xff)
    
    def display(self):  # Device specific display
        #print('Display updating')
        if self.display_type == 'EPD_2in13_V3':
            self.epd.display(self.epd.buffer)
        elif self.display_type == 'EPD_2in13_B_V4':
            self.epd.display()

    def roundTraditional(self,val,digits):
        '''Rounding like you learned in Math'''
        return round(val+10**(-len(str(val))-1), digits)

    def load_image(self,filename):  # inverted pbm files
        # Source: https://blog.miguelgrinberg.com/post/micropython-and-the-internet-of-things-part-vi-working-with-a-screen
        '''Load PBM Image to Display Buffer'''
        with open(filename, 'rb') as f:
            f.readline()
            f.readline()
            width, height = [int(v) for v in f.readline().split()]
            data = bytearray(f.read())
        return framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

    def update_number(self, temp=None, x=0):
        '''Update Display Numbers'''
        text = str(temp)
        if len(text) is 3:  # Temps above 99 do not display properly using GothamBlack_54
            # wget -O GothamBlack_46_Number.py https://raw.githubusercontent.com/bgant/micropython/main/projects/monitor_pool/GothamBlack_46_Numbers.py
            import GothamBlack_46_Numbers
            font_writer = Writer(self.epd, GothamBlack_46_Numbers, verbose=False)
        else:
            font_writer = Writer(self.epd, GothamBlack_54_Numbers, verbose=False)
        textlen = font_writer.stringlen(text)
        Writer.set_textpos(self.epd, x, (self.epd.EPD_WIDTH - textlen) // 2)
        self.epd.rect(6,x,self.epd.EPD_WIDTH-12,55,0xff,True)  # Draw White Rectangle before updated number is displayed
        font_writer.printstring(text, invert=True)


    def update_text(self, text=None, x=0):
        '''Update Display Text'''
        font_writer = Writer(self.epd, GothamBlack_25, verbose=False)
        textlen = font_writer.stringlen(text)
        Writer.set_textpos(self.epd, x, (self.epd.EPD_WIDTH - textlen) // 2)
        font_writer.printstring(text, invert=True)


    def update(self, water=None, air=None, power=True, x=0):
        '''Main Display Update Function'''
        try:
            self.epd.cs_pin(0)  # Select Shared SPI Peripheral
            self.epd.spi.init(phase=0)  # Waveshare uses phase=0 and MAX31856 uses phase=1
            self.epd.init()
            #self.epd.TurnOnDisplay()
            #self.epd.delay_ms(2000)
            if not power:
                print('Power Disconnected...')
                self.fill()  # Fill buffer with white space
                self.epd.blit(self.load_image('graphic_no_power_100px.pbm'), (self.epd.EPD_WIDTH - 100) // 2, (self.epd.EPD_HEIGHT - 100) // 2)
                self.display()
            else:
                self.fill()  # Fill buffer with white space
                # Display pool graphic:
                self.epd.blit(self.load_image('graphic_pool_122px.pbm'), 0, 0)
                # Display Water information:
                if not water or type(water) is str:  # None or Thermocouple Fault String
                    self.epd.blit(self.load_image('graphic_fault_100px.pbm'), (self.epd.EPD_WIDTH - 100) // 2, 150)
                elif water:
                    self.update_number(temp=str(int(self.roundTraditional(water,0))), x=160)
                    self.update_text(text='water', x=220)
                # Display Air information:
                if air is 'no wifi':
                    self.epd.blit(self.load_image('graphic_no_wifi_100px.pbm'), (self.epd.EPD_WIDTH - 100) // 2, 15)
                elif air:
                    self.update_number(temp=str(int(self.roundTraditional(air,0))), x=45)
                    self.update_text(text='feels like', x=15)
                self.display()
        finally:
            print('Display: Deep Sleep .', end='')
            self.epd.ReadBusy()
            self.epd.send_command(0x10)  # Deep Sleep mode Control
            self.epd.send_data(0x01)     # Enter Deep Sleep Mode 1
            #self.epd.sleep()    # Display enters Deep Sleep Mode 01 / To wake call reset() or init()
            self.epd.spi.deinit()
            self.epd.cs_pin(1)  # Deselect Shared SPI Peripheral


'''
NOTES:
    - epd.blit function is inherited from the framebuf.FrameBuffer class in Pico_ePaper_2in13_B_V4.py
'''