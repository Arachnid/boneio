# available_pins.py - Alexander Hiam
# Prints all the pins available for IO expansion by their 
# names used in PyBBIO (refer to beaglebone schematic for
# header locations).
#
# This example is in the public domain

# Import boneio library:
from boneio import *

def main():
  init()

  print "\n GPIO pins:" 
  for i in GPIO.keys(): 
    print "   %s" % i
  print "\n ADC pins:" 
  for i in ADC.keys():
    print "   %s" % i

  cleanup()

if __name__ == '__main__':
  main()
