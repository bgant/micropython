import pool_water
from EPD_2in13_V3 import EPD_2in13_V3_Portrait, EPD_WIDTH, EPD_HEIGHT
import GothamBlack_54_Numbers
import framebuf
from writer_peterhinch import Writer

epd = EPD_2in13_V3_Portrait()

epd.Clear()
epd.fill(0xff)
epd.display(epd.buffer)

def update_temp(temp=None, x=0):
    epd.rect(5,x,EPD_WIDTH-10,55,0xff,True)
    text = str(temp)
    font_writer = Writer(epd, GothamBlack_54_Numbers)
    textlen = font_writer.stringlen(text)
    Writer.set_textpos(epd, x, (EPD_WIDTH - textlen) // 2)
    font_writer.printstring(text, invert=True)
    epd.display_Partial(epd.buffer)

epd.init()
update_temp(temp='75', x=0)
epd.delay_ms(2000)
epd.sleep()
