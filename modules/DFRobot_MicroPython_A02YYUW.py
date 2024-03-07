'''
  Original Raspberry Pi Script:
      https://github.com/DFRobot/DFRobot_RaspberryPi_A02YYUW
'''

from machine import UART
import time

class DFRobot_A02_Distance:

  ## Board status 
  STA_OK = 0x00
  STA_ERR_CHECKSUM = 0x01
  STA_ERR_SERIAL = 0x02
  STA_ERR_CHECK_OUT_LIMIT = 0x03
  STA_ERR_CHECK_LOW_LIMIT = 0x04
  STA_ERR_DATA = 0x05

  ## last operate status, users can use this variable to determine the result of a function call. 
  last_operate_status = STA_OK

  ## variable 
  distance = 0

  ## Maximum range
  distance_max = 4500
  distance_min = 0
  range_max = 4500

  def __init__(self):
    '''
      @brief    Sensor initialization.
    '''
    self._ser = UART(1, 9600)
    self._ser.init(9600,rx=21)
    if self._ser.any() != True:
      self.last_operate_status = self.STA_ERR_SERIAL

  def set_dis_range(self, min, max):
    self.distance_max = max
    self.distance_min = min

  def getDistance(self):
    '''
      @brief    Get measured distance
      @return    measured distance
    '''
    self._measure()
    return self.distance
  
  def _check_sum(self, l):
    return (l[0] + l[1] + l[2])&0x00ff

  def _measure(self):
    data = [0]*4
    i = 0
    timenow = time.time()

    while (self._ser.any() < 4):
      time.sleep(0.01)
      if ((time.time() - timenow) > 1):
        break
    
    rlt = self._ser.read(self._ser.any())
    #print(rlt)
    
    index = len(rlt)
    if(len(rlt) >= 4):
       index = len(rlt) - 4
       while True:
         try:
           data[0] = ord(rlt[index])
         except:
           data[0] = rlt[index]
         if(data[0] == 0xFF):
           break
         elif (index > 0):
           index = index - 1
         else:
           break
       #print(data)
       if (data[0] == 0xFF):
         try:
           data[1] = ord(rlt[index + 1])
           data[2] = ord(rlt[index + 2])
           data[3] = ord(rlt[index + 3])
         except:
           data[1] = rlt[index + 1]
           data[2] = rlt[index + 2]
           data[3] = rlt[index + 3]
         i = 4
    #print(data)
    if i == 4:
      sum = self._check_sum(data)
      if sum != data[3]:
        self.last_operate_status = self.STA_ERR_CHECKSUM
      else:
        self.distance = data[1]*256 + data[2]
        self.last_operate_status = self.STA_OK
      if self.distance > self.distance_max:
        self.last_operate_status = self.STA_ERR_CHECK_OUT_LIMIT
        self.distance = self.distance_max
      elif self.distance < self.distance_min:
        self.last_operate_status = self.STA_ERR_CHECK_LOW_LIMIT
        self.distance = self.distance_min
    else:
      self.last_operate_status = self.STA_ERR_DATA
    return self.distance

  def watch_frames(self):
    single_byte = bytearray(1)
    frame = bytearray()
    while True:
      single_byte = self._ser.read(1) # Read next byte
      if single_byte:  # True if contains data / False if b''
        frame.extend(single_byte)  # Read bytes into frame bytearray
      elif frame:  # True if frame contains data / False if b''
        #print(frame.hex())
        print(f'{int(frame[1:3].hex(),16)}mm')
        frame = bytearray()  # Reset to b'' for next cycle
        time.sleep(0.300)
      else:
        # frame is b''
        pass
