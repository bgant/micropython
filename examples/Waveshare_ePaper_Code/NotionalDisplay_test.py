
# Source: https://github.com/peterhinch/micropython-font-to-py/issues/25
# Source: https://github.com/JPFrancoia/esp32_devkit_waveshare_eink_screen/blob/master/src/main.py

import GothamBlack_54_Numbers  # https://github.com/peterhinch/micropython-font-to-py
import GothamBlack_25
import framebuf  # https://docs.micropython.org/en/latest/library/framebuf.html
from writer import Writer  # https://github.com/peterhinch/micropython-font-to-py/tree/master/writer
from EPD_2in13_B_V4 import EPD_WIDTH, EPD_HEIGHT, EPD_2in13_B_V4  # https://github.com/waveshareteam/Pico_ePaper_Code/tree/main/python

epd = EPD_2in13_B_V4()
epd.imageblack.fill(0xff)
epd.imagered.fill(0xff)

class NotionalDisplay(framebuf.FrameBuffer):
    def __init__(self, width, height, buffer):
        self.width = width
        self.height = height
        self.buffer = buffer
        self.mode = framebuf.MONO_HLSB
        super().__init__(self.buffer, self.width, self.height, self.mode)

    def show(self):
        ...

buf = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)
my_display = NotionalDisplay(EPD_WIDTH, EPD_HEIGHT, buf)
wri = Writer(my_display, GothamBlack_25)
Writer.set_textpos(my_display, 0, 0)
wri.printstring('85\n', invert=True)
my_display.show()
epd.send_data1(buf)
epd.display()
epd.delay_ms(2000)
epd.sleep()

# This does not seem to work