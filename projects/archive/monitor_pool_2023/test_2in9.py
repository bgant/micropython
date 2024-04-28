from EPD_2in9_B import EPD_2in9_B

def my_text(my_text=None):
    epd = EPD_2in9_B()
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)
    epd.imagered.text(my_text, 0, 55, 0x00)
    epd.display()
    epd.delay_ms(2000)
    epd.sleep()
    print(epd.spi)
    epd.spi.deinit()
    print('Done with Display')

