from EPD_2in13_V3 import EPD_2in13_V3_Landscape
epd = EPD_2in13_V3_Landscape()

def my_text(my_text=None):
    epd.spi.init()
    epd.Clear()
    
    epd.fill(0xff)
    epd.text(str(my_text), 0, 10, 0x00)
    epd.display(epd.buffer)
    #epd.display()
    epd.delay_ms(2000)
    epd.sleep()
    print(epd.spi)
    epd.spi.deinit()
    print('Done with Display')

