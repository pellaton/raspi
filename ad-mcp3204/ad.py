import RPi.GPIO as GPIO 
import time

HIGH = GPIO.HIGH
LOW = GPIO.LOW

MISO = 9
MOSI = 10
SCLK = 11
CS = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)

def __SendClock():
  GPIO.output(SCLK, HIGH)
  GPIO.output(SCLK, LOW)

def __Main():
  GPIO.output(CS, HIGH)
  i = 0
  while True: 
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
    
    if (i < 100):
      i += 1
    else:
      print(value)
      i = 0
    
    # await t_csh
    #time.sleep(1)
  
try:
  __Main()
except KeyboardInterrupt:
  GPIO.cleanup()
