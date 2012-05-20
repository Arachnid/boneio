# switch.py - Alexander Hiam - 2/2012
#
# Uses a switch to toggle the state of two LEDs.
# Demonstrates the use of global variables in Python.
# 
# The circuit:
#  - Momentary switch between 3.3v GPIO1_15
#  - 10k ohm resistor from GPIO1_15 to ground
#  - Green LED from GPIO1_17 through 330 ohm resistor to ground
#  - Red LED from GPIO3_21 through 330 ohm resistor to ground
#
# This example is in the public domain

# Import boneio library:
from boneio import *

SWITCH  = GPIO1_15 # P8.15
LED_GRN = GPIO1_17 # P9.23
LED_RED = GPIO3_21 # P9.25

def main():
  init()
  
  # Set the switch as input:
  pinMode(SWITCH, INPUT)
  # Set the LEDs as outputs:
  pinMode(LED_GRN, OUTPUT)
  pinMode(LED_RED, OUTPUT)

  LED_STATE = 0 # 0=green LED lit, 1=red LED lit.
  SW_STATE  = 0 # =1 when switch pressed; only change LED_STATE
                # once per press.

  try:
    while True:
      if digitalRead(SWITCH):
        if SW_STATE == 0:
          # Just pressed, not held down.
          # Set SW_STATE and toggle LED_STATE
          SW_STATE = 1 
          LED_STATE ^= 1
        # Otherwise switch is held down, don't do anything.
      else:
        # Switch not pressed, reset SW_STATE:
        SW_STATE = 0

      if LED_STATE == 0:
        digitalWrite(LED_GRN, True)
        digitalWrite(LED_RED, False)
      else:
        digitalWrite(LED_GRN, False)
        digitalWrite(LED_RED, True)
      # It's good to put a bit of a delay in if possible
      # to keep the processor happy:
      delay(50)
  finally:
    cleanup()

if __name__ == '__main__':
  main()
