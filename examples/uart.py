#Source: 013 - ESP32 MicroPython: UART Serial in MicroPython (YouTube Video)
from machine import Pin, UART
led = Pin(2, Pin.OUT)

# UART0 sends REPL to USB by default
# UART1 is sometimes used to control onboard Flash RAM
# UART2 is usually available to the user
# ESP32 uses GPIO Matrix which allows UART pings to use any available GPIO Pins
#   You must set the tx and rx pins when using UART1 and UART2 on a TinyPICO
uart = UART(2, 115200, tx=18, rx=19)

strMsg = ''
while True:
    if uart.any() > 0:
        strMsg = uart.read()
        print(strMsg)

        if 'on' in strMsg:
            led.on()
            uart.write('Turning ON led\r\n')
            print('Turning ON led')
        elif 'off' in strMsg:
            led.off()
            uart.write('Turning OFF led\r\n')
            print('Turning OFF led')
        else:
            uart.write('Invalid led command\r\n')
            print('Invalid led command')

