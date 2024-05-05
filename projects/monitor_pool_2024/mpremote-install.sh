#!/bin/bash
#
# This script copies all the files needed for this project onto a TinyPICO or TinyS3.
# 
TTY=a0

mpremote $TTY mip install --target= github:bgant/micropython/projects/monitor_pool_2024
mpremote $TTY mip install --target= github:bgant/micropython/modules/key_store.py
mpremote $TTY mip install --target= github:bgant/micropython/modules/wifi.py
mpremote $TTY mip install --target= github:bgant/micropython/modules/webdis.py

mpremote $TTY mip install --target= https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/aiorepl/aiorepl.py

# Added these into my repo just in case they change significantly:
#mpremote $TTY mip install --target= github:peterhinch/micropython-font-to-py/writer/writer.py
#mpremote $TTY mip install --target= github:eliotb/micropython-max31856/max31856.py


