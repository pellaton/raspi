#!/usr/bin/python3

import time
import smbus

from smbus import SMBus
address = 0x39
control_on = 0x03
control_off= 0x00

TSL2561 = SMBus(1)

def __Enable():
  print('Power On')
  TSL2561.write_byte_data(address, 0x80, control_on)
 # TSL2561.write_byte_data(address, 0x81, 0x01)
  time.sleep(0.5)

def __Disable():
  print('Power Off')
  TSL2561.write_byte_data(address, 0x80, control_off)

def __Light():
  ch0 = 16*TSL2561.read_word_data(address, 0xAC)
  ch1 = 16*TSL2561.read_word_data(address, 0xAE)
 
  lux = 0
  if ch1!=0 and ch0 != 0:  
    ratio = ch1 / ch0 
    if(ratio <= 0.5):
      print('1 ', ratio)
      lux=0.0304*ch0-0.062*ch0*(ratio**1.4)
    elif (ratio <= 0.61):
      print('2 ', ratio)
      lux=0.0224*ch0-0.031*ch1
    elif (ratio <= 0.80):
      print('3 ', ratio)
      lux=0.0128*ch0-0.0153*ch1
    elif (ratio <= 1.30):
      print('4 ', ratio)
      lux=0.00146*ch0-0.00112*ch1

  print('TOTAL light: %5d IR LIGHT: %5d' % (ch0,ch1))
  print('LUX: %5f' % lux) 

def __Main():
  __Enable()
  __Light()
  __Disable()  
  
__Main()
