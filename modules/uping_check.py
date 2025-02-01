from machine import reset
from time import sleep

try:
    import uping
except OSError:
    print('uping.py required to use this module')
    exit()

wait_time = 15  # Wait X seconds before rebooting device


def network_fail():
    print('Unable to access network... resetting...')
    sleep(wait_time)
    reset()

def ping_check(target=None):
    if not target:
        print("You need to specify a host to ping: ping_check('8.8.4.4') or ping_check(wifi.gateway)")
        return
    try:
        pong = uping.ping(target,quiet=True)
        if not pong[1]:  # Zero packets received
            network_fail()
            return False
        return True
    except:
        network_fail()   # Ping could not resolve name or access network
        return False

def network_fail():
    print('Unable to access network... resetting...')
    sleep_ms(wait_time)
    reset()

