#!/bin/bash
#
# This script copies all the files needed for this project onto a TinyPICO or TinyS3.
# 

DEVICE=u0

mpremote $DEVICE mip install --target= github:bgant/micropython/projects/monitor_aqi/main.py
mpremote $DEVICE mip install --target= github:bgant/micropython/modules/key_store.py
mpremote $DEVICE mip install --target= github:bgant/micropython/modules/wifi.py
mpremote $DEVICE mip install --target= github:bgant/micropython/modules/webdis.py

mpremote $DEVICE mip install --target= https://raw.githubusercontent.com/pkucmus/micropython-pms7003/master/pms7003.py
mpremote $DEVICE mip install --target= https://raw.githubusercontent.com/pkucmus/micropython-pms7003/master/aqi.py
