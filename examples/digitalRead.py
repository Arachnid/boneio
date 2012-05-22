# digitalRead.py - Alexander Hiam - 2/2012
# USR3 LED mirrors GPIO1_6 until CTRL-C is pressed.
#
# This example is in the public domain

# Import boneio library:
from boneio import *

def main():
  init()

  # Set the GPIO pins:
  USR3.output()
  GPIO1_6.input()

  try:
    while True:
      state = GPIO1_6.value
      USR3.value = state
      # It's good to put a bit of a delay in if possible
      # to keep the processor happy:
      delay(100)
  finally:
    cleanup()
    
if __name__ == '__main__':
  main()
