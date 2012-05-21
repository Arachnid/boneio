# blink.py - Alexander Hiam - 2/2012
# Blinks two of the Beagleboard's on-board LEDs until CTRL-C is pressed.
#
# This example is in the public domain

# Import boneio library:
from boneio import *

def main():
  init()

  # Set the two LEDs as outputs:
  USR2.output()
  USR3.output()

  # Start one high and one low:
  USR2.set()
  USR3.clear()

  try:
    while True:
      # Toggle the two LEDs and sleep a few seconds:
      USR2.toggle()
      USR3.toggle()
      delay(500)
  finally:
    cleanup()

if __name__ == '__main__':
  main()
