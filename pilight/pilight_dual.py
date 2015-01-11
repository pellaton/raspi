#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import datetime
import signal
import sys

from math import *

HIGH = GPIO.HIGH
LOW = GPIO.LOW

# GPIO Pins
MISO = 9
MOSI = 10
SCLK = 11
CS = 25
PWR = 18
LAMP_ON = 4
LAMP_OFF = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(PWR, GPIO.OUT)
GPIO.setup(LAMP_ON, GPIO.OUT) 
GPIO.setup(LAMP_OFF, GPIO.OUT) 

# 'a': append to existing file
logFile = open('/var/log/pilight.log', 'a')

def __ActuateSwitch(pin):
  GPIO.output(pin, HIGH)
  time.sleep(0.2)
  GPIO.output(pin, LOW)

def __SwitchLampOn():
  __ActuateSwitch(LAMP_ON)

def __SwitchLampOff():
  __ActuateSwitch(LAMP_OFF)

def __SendClock():
  GPIO.output(SCLK, HIGH)
  GPIO.output(SCLK, LOW)

def __ReadValue(channel):
  GPIO.output(CS, HIGH)
  # enable chip
  GPIO.output(CS, LOW)

  # send command : start start = 1, single=1, channel=000 
  sendcmd = 0b00011000 | channel
  for commandBits in range(5):
    if (sendcmd & 0x10):
      GPIO.output(MOSI, HIGH)
    else:
      GPIO.output(MOSI, LOW)
    __SendClock()
    sendcmd <<= 1
      
  # readout
  value = 0
  for dataBits in range(13):
    __SendClock()
    value <<= 1
    if (GPIO.input(MISO)):
      value |= 0x01

  # disbale chip
  GPIO.output(CS, HIGH)

  return value
 
def __MeasureBrightness():
  sumValue = [0.0, 0.0]
  samplePoints = 10
 
  GPIO.output(PWR, HIGH)
  for i in range(samplePoints):
    value0 = __ReadValue(0)
    value1 = __ReadValue(1)
    sumValue[0] += value0;
    sumValue[1] += value1;

  GPIO.output(PWR, LOW)

  return [sumValue[0]/samplePoints, sumValue[1]/samplePoints] 

def __WriteLog(dateTime, brightnessOn, brightnessOff):
  print(dateTime.isoformat(), '{:6.1f}'.format(brightnessOn[0]),'{:6.1f}'.format(brightnessOn[1]),
  '{:6.1f}'.format(brightnessOff[0]),'{:6.1f}'.format(brightnessOff[1]),
  file=logFile) 
  logFile.flush()

def __cleanup():
  GPIO.cleanup()
  print('#', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PiLight stopped', file=logFile) 
  logFile.close()
  sys.exit(0)

def __Main():
  print('#',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PiLight started', file=logFile) 
  while(True):
    now = datetime.datetime.now()
    if (now.hour >= 7 and now.hour <= 21 ):
      __SwitchLampOff()
      time.sleep(5)
      brightnessOff = __MeasureBrightness()
      __SwitchLampOn()
      time.sleep(5)
      brightnessOn = __MeasureBrightness()
      __WriteLog(now, brightnessOn, brightnessOff)
    else:
      __SwitchLampOff()
      brightness = __MeasureBrightness()
      __WriteLog(now, [0,0], brightness)
    time.sleep(10*60-10)

try:
  signal.signal(signal.SIGINT, __cleanup)
  signal.signal(signal.SIGTERM, __cleanup)
  __Main()
finally:
  __cleanup()
