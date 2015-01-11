import RPi.GPIO as GPIO 
import time
import signal

HIGH = GPIO.HIGH
LOW = GPIO.LOW

GPIO.setmode(GPIO.BCM)
def __cleanup():
  GPIO.cleanup()
  sys.exit(0)

def __Main():
  
try:
  signal.signal(signal.SIGINT, __cleanup)
  signal.signal(signal.SIGTERM, __cleanup)
  __Main()
finally:
  __cleanup()
