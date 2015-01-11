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
log_file = open('/var/log/pilight2.log', 'a')

def actuate_switch(pin):
  GPIO.output(pin, HIGH)
  time.sleep(0.2)
  GPIO.output(pin, LOW)

def switch_lamp_on():
  actuate_switch(LAMP_ON)

def switch_lamp_off():
  actuate_switch(LAMP_OFF)

def send_clock():
  GPIO.output(SCLK, HIGH)
  GPIO.output(SCLK, LOW)

def read_value(channel):
  GPIO.output(CS, HIGH)
  # enable chip
  GPIO.output(CS, LOW)

  # send command : start start = 1, single=1, channel=000 
  send_cmd = 0b00011000 | channel
  for command_bits in range(5):
    if (send_cmd & 0x10):
      GPIO.output(MOSI, HIGH)
    else:
      GPIO.output(MOSI, LOW)
    send_clock()
    send_cmd <<= 1
      
  # readout
  value = 0
  for data_bits in range(13):
    send_clock()
    value <<= 1
    if (GPIO.input(MISO)):
      value |= 0x01

  # disbale chip
  GPIO.output(CS, HIGH)

  return value
 
def measure_brightness():
  sum_value = [0.0, 0.0]
  sample_points = 10
 
  GPIO.output(PWR, HIGH)
  for i in range(sample_points):
    value_0 = read_value(0)
    value_1 = read_value(1)
    sum_value[0] += value_0
    sum_value[1] += value_1

  GPIO.output(PWR, LOW)

  return [sum_value[0]/sample_points, sum_value[1]/sample_points] 

def write_log(date_time, brightness_out, brightness_in, lamp_state):
  print(date_time.isoformat(), '{:6.1f}'.format(brightness_out),
  '{:6.1f}'.format(brightness_in), lamp_state,  file=log_file) 
  log_file.flush()

def cleanup():
  GPIO.cleanup()
  print('#', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PiLight stopped', file=log_file) 
  log_file.close()
  sys.exit(0)

def main():
  print('#',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PiLight started', file=log_file) 
  while(True):
    now = datetime.datetime.now()
    brightness_out, brightness_in = measure_brightness()
    if (now.hour >= 7 and now.hour < 21 ):
      if (brightness_out <= 3450):
        write_log(now, brightness_out, brightness_in, 'on')
        switch_lamp_on()
      elif (brightness_out >= 3750):
        write_log(now, brightness_out, brightness_in, 'off')
        switch_lamp_off()
      else:
        write_log(now, brightness_out, brightness_in, 'n/a')
    else:
      switch_lamp_off()
      write_log(now, brightness_out, brightness_in, 'off')
    time.sleep(10*60)

try:
  signal.signal(signal.SIGINT, cleanup)
  signal.signal(signal.SIGTERM, cleanup)
  main()
finally:
  cleanup()
