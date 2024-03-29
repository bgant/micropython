# Source: https://pycom.io/get-started-subscribing-and-publishing-messages-in-micropython-using-mqtt/

from network import WLAN 
from mqtt import MQTTClient 
import machine 
import time 
 
def sub_cb(topic, msg): 
   print(msg) 
 
wlan = WLAN(mode=WLAN.STA) 
wlan.connect("yourwifinetwork", auth=(WLAN.WPA2, "wifipassword"), timeout=5000) 
 
while not wlan.isconnected():  
    machine.idle() 
print("Connected to Wifin") 
 
client = MQTTClient("device_id", "io.adafruit.com",user="your_username", password="your_api_key", port=1883) 
client.set_callback(sub_cb) 
client.connect()
client.subscribe(topic="youraccount/feeds/lights") 
while True: 
    print("Sending ON") 
    client.publish(topic="youraccount/feeds/lights", msg="ON")
    time.sleep(1) 
    print("Sending OFF") 
    client.publish(topic="youraccount/feeds/lights", msg="OFF")
    
    time.sleep(1) 

