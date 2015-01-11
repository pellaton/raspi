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

def __ReadValue():
  GPIO.output(CS, HIGH)
  # enable chip
  GPIO.output(CS, LOW)

  # send command : start start = 1, single=1, channel=000 
  sendcmd = 0b00011000
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
  sumValue = 0.0
  samplePoints = 10
 
  GPIO.output(PWR, HIGH)
  for i in range(samplePoints):
    value = __ReadValue()
    sumValue += value;

  GPIO.output(PWR, LOW)

  return sumValue / samplePoints

def __WriteLog(dateTime, brightness, lampState):
  print(dateTime.strftime("%Y-%m-%d %H:%M:%S"), '{:6.1f}'.format(brightness), lampState, file=logFile) 
  logFile.flush()

def __cleanup():
  GPIO.cleanup()
  print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PiLight stopped', file=logFile) 
  logFile.close()
  sys.exit(0)

def __Main():
  print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PiLight started', file=logFile) 
  while(True):
    now = datetime.datetime.now()
    if (now.hour >= 7 and now.hour < 21 ):
      brightness = __MeasureBrightness()
      if (brightness <= 2500):
        __WriteLog(now, brightness, 'on')
        __SwitchLampOn()
      elif (brightness >= 3000):
        __WriteLog(now, brightness, 'off')
        __SwitchLampOff()
      else:
        __WriteLog(now, brightness, 'n/a')
    else:
      __WriteLog(now, -1.0, 'off')
      __SwitchLampOff()
    time.sleep(5*60)

try:
  signal.signal(signal.SIGINT, __cleanup)
  signal.signal(signal.SIGTERM, __cleanup)
  __Main()
finally:
  __cleanup()
