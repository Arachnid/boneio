"""
 PyBBIO - bbio.py - v0.3.1
 Created: 12/2011
 Author: Alexander Hiam - ahiam@marlboro.edu - www.alexanderhiam.com
 Website: https://github.com/alexanderhiam/PyBBIO

 A Python library for hardware IO support on the TI Beaglebone.
 Currently only supporting basic digital and analog IO, but more 
 peripheral support is on the way, so keep checking the Github page
 for updates.

 16-bit register support mod from sbma44 - https://github.com/sbma44

 Copyright 2012 Alexander Hiam

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import struct, os, sys, time
from mmap import mmap


# Load platform configuration
# TODO(arachnid): Support multiple platforms
# TODO(arachnid): Move stuff out of global namespace
from platforms.beaglebone import *

# Create global mmap:
with open("/dev/mem", "r+b") as f:
  __mmap = mmap(f.fileno(), MMAP_SIZE, offset=MMAP_OFFSET)


# TODO(arachnid): Refactor all this into a class so setup and cleanup are
#     handled neatly.
def init():
  """ Pre-run initialization, i.e. starting module clocks, etc. """
  _analog_init()


def _analog_init():
  """ Initializes the on-board 8ch 12bit ADC. """
  step_config = 'ADCSTEPCONFIG%i'
  #step_delay = 'ADCSTEPDELAY%i'
  ain = 'AIN%i'   
  # Enable ADC module clock:
  _setReg(CM_WKUP_ADC_TSC_CLKCTRL, MODULEMODE_ENABLE)
  # Wait for enable complete:
  while (_getReg(CM_WKUP_ADC_TSC_CLKCTRL) & IDLEST_MASK): time.sleep(0.1)
  # Must turn off STEPCONFIG write protect:
  _andReg(ADC_CTRL, ADC_STEPCONFIG_WRITE_PROTECT(0))
  # Set STEPCONFIG1-STEPCONFIG8 to correspond to ADC inputs 0-7:
  for i in xrange(8):
    config = SEL_INP(ain % i) | ADC_AVG4 # Average 4 readings
    _andReg(eval(step_config % (i+1)), config)
  # Now we can enable ADC subsystem, re-enabling write protect:
  _setReg(ADC_CTRL, TSC_ADC_SS_ENABLE)

def cleanup():
  """ Post-run cleanup, i.e. stopping module clocks, etc. """
  _analog_cleanup()
  _serial_cleanup()
  __mmap.close()

def _analog_cleanup():
  # Disable ADC subsystem:
  _clearReg(ADC_CTRL, TSC_ADC_SS_ENABLE)
  # Disable ADC module clock:
  _clearReg(CM_WKUP_ADC_TSC_CLKCTRL, MODULEMODE_ENABLE)

def _serial_cleanup():
  """ Ensures that all serial ports opened by current process are closed. """
  for port in (Serial1, Serial2, Serial4, Serial5):
    port.end()

def delay(ms):
  """ Sleeps for given number of milliseconds. """
  time.sleep(ms/1000.0)

def delayMicroseconds(us):
  """ Sleeps for given number of microseconds > ~30; still working 
      on a more accurate method. """
  t = time.time()
  while (((time.time()-t)*1000000) < us): pass

def pinMode(gpio_pin, direction, pull=-1):
  """ Sets given digital pin to input if direction=1, output otherwise.
      'pull' will set the pull up/down resitsor if setting as an input:
      pull=-1 for pull-down, pull=1 for pull up, pull=0 for none. """
  assert (gpio_pin in GPIO), "*Invalid GPIO pin: '%s'" % gpio_pin
  if (direction == INPUT):
    # Pinmux:
    if (pull > 0): pull = CONF_PULLUP
    elif (pull == 0): pull = CONF_PULL_DISABLE
    else: pull = 0
    _pinMux(GPIO[gpio_pin][2], CONF_GPIO_INPUT|pull)
    # Set input:
    _orReg(GPIO[gpio_pin][0]+GPIO_OE, GPIO[gpio_pin][1])
    return
  # Pinmux:
  _pinMux(GPIO[gpio_pin][2], CONF_GPIO_OUTPUT)
  # Set output:
  _clearReg(GPIO[gpio_pin][0]+GPIO_OE, GPIO[gpio_pin][1])

def digitalWrite(gpio_pin, state):
  """ Writes given digital pin low if state=0, high otherwise. """
  assert (gpio_pin in GPIO), "*Invalid GPIO pin: '%s'" % gpio_pin
  if (state):
    _orReg(GPIO[gpio_pin][0]+GPIO_DATAOUT, GPIO[gpio_pin][1])
    return
  _clearReg(GPIO[gpio_pin][0]+GPIO_DATAOUT, GPIO[gpio_pin][1])

def toggle(gpio_pin):
  """ Toggles the state of the given digital pin. """
  assert (gpio_pin in GPIO), "*Invalid GPIO pin: '%s'" % gpio_pin
  _xorReg(GPIO[gpio_pin][0]+GPIO_DATAOUT, GPIO[gpio_pin][1])

def digitalRead(gpio_pin):
  """ Returns pin state as 1 or 0. """
  assert (gpio_pin in GPIO), "*Invalid GPIO pin: '%s'" % gpio_pin
  if (_getReg(GPIO[gpio_pin][0]+GPIO_DATAIN) & GPIO[gpio_pin][1]):
    return 1
  return 0

def pinState(gpio_pin):
  """ Returns the state of a digital pin if it is configured as
      an output. Returns None if it is configuredas an input. """
  assert (gpio_pin in GPIO), "*Invalid GPIO pin: '%s'" % gpio_pin
  if (_getReg(GPIO[gpio_pin][0]+GPIO_OE) & GPIO[gpio_pin][1]):
    return None
  if (_getReg(GPIO[gpio_pin][0]+GPIO_DATAOUT) & GPIO[gpio_pin][1]):
    return HIGH
  return LOW

def analogRead(analog_pin):
  """ Returns analog value read on given analog input pin. """
  assert (analog_pin in ADC), "*Invalid analog pin: '%s'" % analog_pin

  if (_getReg(CM_WKUP_ADC_TSC_CLKCTRL) & IDLEST_MASK):
    # The ADC module clock has been shut off, e.g. by a different 
    # PyBBIO script stopping while this one was running, turn back on:
    _analog_init() 

  _orReg(ADC_STEPENABLE, ADC_ENABLE(analog_pin))
  while(_getReg(ADC_STEPENABLE) & ADC_ENABLE(analog_pin)): pass
  return _getReg(ADC_FIFO0DATA)&ADC_FIFO_MASK

def _pinMux(fn, mode):
  """ Uses kernel omap_mux files to set pin modes. """
  # There's no simple way to write the control module registers from a 
  # user-level process because it lacks the proper privileges, but it's 
  # easy enough to just use the built-in file-based system and let the 
  # kernel do the work. 
  try:
    with open(PINMUX_PATH+fn, 'wb') as f:
      f.write(hex(mode)[2:]) # Write hex string (stripping off '0x')
  except IOError:
    print "*omap_mux file not found: '%s'" % (PINMUX_PATH+fn)

def _andReg(address, mask, length=32):
  """ Sets 16 or 32 bit Register at address to its current value AND mask. """
  _setReg(address, _getReg(address, length)&mask, length)

def _orReg(address, mask, length=32):
  """ Sets 16 or 32 bit Register at address to its current value OR mask. """
  _setReg(address, _getReg(address, length)|mask, length)

def _xorReg(address, mask, length=32):
  """ Sets 16 or 32 bit Register at address to its current value XOR mask. """
  _setReg(address, _getReg(address, length)^mask, length)

def _clearReg(address, mask, length=32):
  """ Clears mask bits in 16 or 32 bit register at given address. """
  _andReg(address, ~mask, length)

def _getReg(address, length=32):
  """ Returns unpacked 16 or 32 bit register value starting from address. """
  if (length == 32):
    return struct.unpack("<L", __mmap[address:address+4])[0]
  elif (length == 16):
    return struct.unpack("<H", __mmap[address:address+2])[0]
  else:
    raise ValueError("Invalid register length: %i - must be 16 or 32" % length)

def _setReg(address, new_value, length=32):
  """ Sets 16 or 32 bits at given address to given value. """
  if (length == 32):
    __mmap[address:address+4] = struct.pack("<L", new_value)
  elif (length == 16):
    __mmap[address:address+2] = struct.pack("<H", new_value)
  else:
    raise ValueError("Invalid register length: %i - must be 16 or 32" % length)



# TODO(arachnid): Slim this down into a basic wrapper that handles pinmux
  
# _UART_PORT is a wrapper class for pySerial to enable Arduino-like access
# to the UART1, UART2, UART4, and UART5 serial ports on the expansion headers:
class _UART_PORT(object):
  def __init__(self, uart):
    assert uart in UART, "*Invalid UART: %s" % uart
    self.config = uart
    self.baud = 0
    self.open = False
    self.ser_port = None
    self.peek_char = ''

  def begin(self, baud, timeout=1):
    import serial

    """ Starts the serial port at the given baud rate. """
    # Set proper pinmux to match expansion headers:
    tx_pinmux_filename = UART[self.config][1]
    tx_pinmux_mode     = UART[self.config][2]+CONF_UART_TX
    _pinMux(tx_pinmux_filename, tx_pinmux_mode)

    rx_pinmux_filename = UART[self.config][3]
    rx_pinmux_mode     = UART[self.config][4]+CONF_UART_RX
    _pinMux(rx_pinmux_filename, rx_pinmux_mode)    

    port = UART[self.config][0]
    self.baud = baud
    self.ser_port = serial.Serial(port, baud, timeout=timeout)
    self.open = True 

  def end(self):
    """ Closes the serial port if open. """
    if not(self.open): return
    self.flush()
    self.ser_port.close()
    self.ser_port = None
    self.baud = 0
    self.open = False

  def available(self):
    """ Returns the number of bytes currently in the receive buffer. """
    return self.ser_port.inWaiting() + len(self.peek_char)

  def read(self):
    """ Returns first byte of data in the receive buffer or -1 if none. """
    if (self.peek_char):
      c = self.peek_char
      self.peek_char = ''
      return c
    if self.available():
      return self.ser_port.read(1)
    return -1

  def peek(self):
    """ Returns the next char from the receive buffer without removing it, 
        or -1 if no data available. """
    if (self.peek_char):
      return self.peek_char
    if self.available():
      self.peek_char = self.ser_port.read(1)
      return self.peek_char
    return -1    

  def flush(self):
    """ Waits for current write to finish then flushes rx/tx buffers. """
    self.ser_port.flush()
    self.peek_char = ''

  def prints(self, data, base=None):
    """ Prints string of given data to the serial port. Returns the number
        of bytes written. The optional 'base' argument is used to format the
        data per the Arduino serial.print() formatting scheme, see:
        http://arduino.cc/en/Serial/Print """
    return self.write(self._process(data, base))

  def println(self, data, base=None):
    """ Prints string of given data to the serial port followed by a 
        carriage return and line feed. Returns the number of bytes written.
        The optional 'base' argument is used to format the data per the Arduino
        serial.print() formatting scheme, see: http://arduino.cc/en/Serial/Print """
    return self.write(self._process(data, base)+"\r\n")

  def write(self, data):
    """ Writes given data to serial port. If data is list or string each
        element/character is sent sequentially. If data is float it is 
        converted to an int, if data is int it is sent as a single byte 
        (least significant if data > 1 byte). Returns the number of bytes
        written. """
    assert self.open, "*%s not open, call begin() method before writing" %\
                      UART[self.config][0]

    if (type(data) == float): data = int(data)
    if (type(data) == int): data = chr(data & 0xff)

    elif ((type(data) == list) or (type(data) == tuple)):
      bytes_written = 0
      for i in data:
        bytes_written += self.write(i)  
      return bytes_written

    else:
      # Type not supported by write, e.g. dict; use prints().
      return 0

    written = self.ser_port.write(data)
    # Serial.serial.write() returns None if no bits written, we want 0:
    return written if written else 0

  def _process(self, data, base):
    """ Processes and returns given data per Arduino format specified on 
        serial.print() page: http://arduino.cc/en/Serial/Print """
    if (type(data) == str):
      # Can't format if already a string:
      return data

    if (type(data) is int):
      if not (base): base = DEC # Default for ints
      if (base == DEC):
        return str(data) # e.g. 20 -> "20"
      if (base == BIN):
        return bin(data)[2:] # e.g. 20 -> "10100"
      if (base == OCT):
        return oct(data)[1:] # e.g. 20 -> "24"
      if (base == HEX):
        return hex(data)[2:] # e.g. 20 -> "14"

    elif (type(data) is float):
      if not (base): base = 2 # Default for floats
      if ((base == 0)):
        return str(int(data))
      if ((type(base) == int) and (base > 0)):
        return ("%0." + ("%i" % base) + "f") % data

    # If we get here data isn't supported by this formatting scheme,
    # just convert to a string and return:
    return str(data)

# Initialize the global serial port instances:
Serial1 = _UART_PORT('UART1')
Serial2 = _UART_PORT('UART2')
Serial4 = _UART_PORT('UART4')
Serial5 = _UART_PORT('UART5')
