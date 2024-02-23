# MicroPython WiFi
These are the scripts I use on ESP32 and TinyPICO boards to get WiFi up and running using the boot.py script.

## boot.py
In MicroPython `boot.py` is run first, then the `main.py` script. With this script I get WiFi connected, run NTP to set the clock (if needed), and then print some info about the RAM, filesystem, and the files currently on disk.

This `boot.py` script will not run without the `key_store.py` script.

## key_store.py - Key/Value Pairs stored on Disk
I wrote this script to create a btree database of Key/Value Pairs on disk that survive reboots. It is mainly used to store the WiFi SSID and Password, but it can also be used to store any information like API keys or IP addresses of local servers. It might be better to just use a file containing a dictionary variable of key/value pairs, but I have not had any troubles with corruption using btree.

## timezone.py - Local Timezone in MicroPython
If you update the time on your device over WiFi using the Network Time Protocol (NTP), the `time.localtime()` command will give you [Coordinated Universal Time (UTC)](https://www.timeanddate.com/time/aboututc.html). This is usually the best standard to use in your projects to avoid switching back and forth between your own Standard Time and Daylight Savings Time, but sometimes you really need to use your own local time.

The `timezone.py` [MicroPython](https://micropython.org/) module converts UTC to [Central Standard Time (CST)](https://www.timeanddate.com/time/zones/cdt) or [Central Daylight Time (CDT)](https://www.timeanddate.com/time/zones/cdt), but you can edit the script to enter your own UTC Offset numbers.

```python
import ntptime
ntptime.host = 'pool.ntp.org'
ntptime.settime() 

import time
from timezone import tz
time.localtime(tz())
```

My Thanks to [Peter Hinch](https://github.com/peterhinch) for providing this code in a [thread](https://forum.micropython.org/viewtopic.php?t=3675#p28989) on the MicroPython Forum.

## TinyPICO_RGB.py
The TinyPICO has a multi-color LED on the board. I use this script to turn the LED purple while the boot.py is connecting to WiFi and then blue when WiFi is connected. 

## detect_filesystem.py
For a while, I had some boards that would become corrupted after running for long periods (I assume due to power outages). These boards were all using a FAT filesystem. I [found this script](https://forum.micropython.org/viewtopic.php?t=7228&start=10) on the MicroPython Forum to display the filesystem during boot which would remind me to convert the disk layout to the much more fault tolerant LittleFS2 filesystem.

Now that MicroPython uses LittleFS2 by default in newer versions, this script should no longer be needed.
