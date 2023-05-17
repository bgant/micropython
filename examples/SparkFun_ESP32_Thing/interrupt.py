# Source: YouTube - Invent Box Tutorials - Learn MicroPython #4 - Interrupts (event-driven code)

from machine import Pin

led = Pin(5, Pin.OUT)  # Sparkfun ESP32 Thing
btn = Pin(0, Pin.IN)

def my_func(pin): 
    if btn() == 0:  # active-low / button pressed
        led.on()
    else:
        led.off()

# Interrupt Request
btn.irq(my_func)

# mpremote u0 cp interrupt.py :
# >>> import interrupt
# REPL is available and the LED turns on when you press button 0

