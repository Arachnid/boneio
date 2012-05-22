# available_pins.py - Alexander Hiam
# Prints all the pins available for IO expansion by their 
# names used in PyBBIO (refer to beaglebone schematic for
# header locations).
#
# This example is in the public domain

# Import boneio library:
import boneio

def main():
  init()

  print "\n GPIO pins:"
  for k in dir(boneio):
      if isinstance(getattr(boneio, k), boneio.GPIO):
          print "   %s" % k
  print "\n ADC pins:" 
  for i in ADC.keys():
    print "   %s" % i

  cleanup()

if __name__ == '__main__':
  main()
