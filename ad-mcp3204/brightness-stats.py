import RPi.GPIO as GPIO 
import time

from math import *

HIGH = GPIO.HIGH
LOW = GPIO.LOW

MISO = 9
MOSI = 10
SCLK = 11
CS = 26
PWR = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(PWR, GPIO.OUT)

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
  
def __Main():
  sumValue = 0.0
  sumSquareValue = 0.0
  minValue = 4096
  maxValue = 0.0

  samplePoints = 1000

  GPIO.output(PWR, HIGH)
  for i in range(samplePoints):
    value = __ReadValue()
    minValue = minValue if minValue < value else value
    maxValue = value if value > maxValue else maxValue
    sumValue += value;
    sumSquareValue += value * value

  GPIO.output(PWR, LOW)

  meanValue = sumValue / samplePoints
  dev = sqrt((sumSquareValue-sumValue*sumValue/samplePoints)/ (samplePoints -1) )  

  print('Mean Value: ', meanValue)
  print('Min Value: ', minValue)
  print('Max Value: ', maxValue)
  print('Deviation: ', dev) 
try:
  __Main()
  GPIO.cleanup()
except KeyboardInterrupt:
  GPIO.cleanup()
