# Usage:
#    from non_blocking_sleep import sleep
#    sleep(5)

from time import ticks_ms

def sleep(duration=1):
    duration *= 1000  # Covert to milliseconds
    start_time = ticks_ms()
    while True:
        if ( ticks_ms() - start_time > duration ):
            return

