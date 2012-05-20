# blink.py - Alexander Hiam - 2/2012
# Blinks two of the Beagleboard's on-board LEDs until CTRL-C is pressed.
#
# This example is in the public domain

# Import boneio library:
from boneio import *

def main():
  init()

  # Set the two LEDs as outputs: 
  pinMode(USR2, OUTPUT)
  pinMode(USR3, OUTPUT)

  # Start one high and one low:
  digitalWrite(USR2, HIGH)
  digitalWrite(USR3, LOW)

  try:
    while True:
      # Toggle the two LEDs and sleep a few seconds:
      toggle(USR2)
      toggle(USR3)
      delay(500)
  finally:
    cleanup()

if __name__ == '__main__':
  main()
