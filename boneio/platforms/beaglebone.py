# Config file for PyBBIO 

#---------------------------------------------------#
# Changes to this file may lead to permanent damage #
# to you Beaglebone, edit with care.                #
#---------------------------------------------------#

from boneio import boneio


registers = boneio.RegisterMap(0x44c00000, end_address=0x48ffffff)

##############################
##--- Start PRCM config: ---##
## Power Management and Clock Module

#--- Module clock control: ---
_CM_WKUP = 0x44e00400-MMAP_OFFSET

_CM_WKUP_ADC_TSC_CLKCTRL = 0xbc+CM_WKUP

_MODULEMODE_ENABLE = 0x02
_IDLEST_MASK = 0x03<<16
# To enable module clock:
#  _setReg(CM_WKUP_module_CLKCTRL, MODULEMODE_ENABLE)
#  while (_getReg(CM_WKUP_module_CLKCTRL) & IDLEST_MASK): pass
# To disable module clock:
#  _andReg(CM_WKUP_module_CLKCTRL, ~MODULEMODE_ENABLE)
#-----------------------------

##--- End PRCM config ------##
##############################

########################################
##--- Start control module config: ---##

class BeagleboneMuxer(boneio.Muxer):
    SLEW_SLOW    = 1<<6
    RX_ACTIVE    = 1<<5
    PULLUP       = 1<<4
    PULL_DISABLE = 1<<3

    GPIO_MODE    = 0x07 
    GPIO_OUTPUT = GPIO_MODE
    GPIO_INPUT  = GPIO_MODE + RX_ACTIVE
    ADC_PIN     = RX_ACTIVE + PULL_DISABLE

    UART_TX     = PULLUP
    UART_RX     = RX_ACTIVE

muxer = BeagleboneMuxer('/sys/kernel/debug/omap_mux/')

##--- End control module config ------##
########################################

##############################
##--- Start GPIO config: ---##
_GPIO0 = 0x44e07000-MMAP_OFFSET
_GPIO1 = 0x4804c000-MMAP_OFFSET
_GPIO2 = 0x481ac000-MMAP_OFFSET
_GPIO3 = 0x481ae000-MMAP_OFFSET

_GPIO_OE           = 0x134
_GPIO_DATAIN       = 0x138
_GPIO_DATAOUT      = 0x13c
_GPIO_CLEARDATAOUT = 0x190
_GPIO_SETDATAOUT   = 0x194

## GPIO pins:

# GPIO pins must be in form: 
#             [GPIO_mux, bit_value, pinmux_filename], e.g.:
# "GPIO1_4" = [   GPIO1,      1<<4,      'gpmc_ad4']  

_gpio = {
      "USR0" : (_GPIO1, 22,           'gpmc_a5'),
      "USR1" : (_GPIO1, 22,           'gpmc_a6'),
      "USR2" : (_GPIO1, 23,           'gpmc_a7'),
      "USR3" : (_GPIO1, 24,           'gpmc_a8'),
   "GPIO0_7" : (_GPIO0,  7, 'ecap0_in_pwm0_out'),
  "GPIO0_26" : (_GPIO0, 26,         'gpmc_ad10'),
  "GPIO0_27" : (_GPIO0, 27,         'gpmc_ad11'),
   "GPIO1_0" : (_GPIO1,     1,          'gpmc_ad0'),
   "GPIO1_1" : (_GPIO1,  1,          'gpmc_ad1'),
   "GPIO1_2" : (_GPIO1,  2,          'gpmc_ad2'),
   "GPIO1_3" : (_GPIO1,  3,          'gpmc_ad3'),
   "GPIO1_4" : (_GPIO1,  4,          'gpmc_ad4'),
   "GPIO1_5" : (_GPIO1,  5,          'gpmc_ad5'),
   "GPIO1_6" : (_GPIO1,  6,          'gpmc_ad6'),
   "GPIO1_7" : (_GPIO1,  7,          'gpmc_ad7'),
  "GPIO1_12" : (_GPIO1, 12,         'gpmc_ad12'),
  "GPIO1_13" : (_GPIO1, 13,         'gpmc_ad13'),
  "GPIO1_14" : (_GPIO1, 14,         'gpmc_ad14'),
  "GPIO1_15" : (_GPIO1, 15,         'gpmc_ad15'),
  "GPIO1_16" : (_GPIO1, 16,           'gpmc_a0'),
  "GPIO1_17" : (_GPIO1, 17,           'gpmc_a1'),
  "GPIO1_28" : (_GPIO1, 28,         'gpmc_ben1'),
  "GPIO1_29" : (_GPIO1, 29,         'gpmc_csn0'),
  "GPIO1_30" : (_GPIO1, 30,         'gpmc_csn1'),
  "GPIO1_31" : (_GPIO1, 31,         'gpmc_csn2'),
   "GPIO2_1" : (_GPIO2,     1,          'gpmc_clk'),
   "GPIO2_6" : (_GPIO2,  6,         'lcd_data0'),
   "GPIO2_7" : (_GPIO2,  7,         'lcd_data1'),
   "GPIO2_8" : (_GPIO2,  8,         'lcd_data2'),
   "GPIO2_9" : (_GPIO2,  9,         'lcd_data3'),
  "GPIO2_10" : (_GPIO2, 10,         'lcd_data4'),
  "GPIO2_11" : (_GPIO2, 11,         'lcd_data5'),
  "GPIO2_12" : (_GPIO2, 12,         'lcd_data6'),
  "GPIO2_13" : (_GPIO2, 13,         'lcd_data7'),
  "GPIO2_22" : (_GPIO2, 22,         'lcd_vsync'),
  "GPIO2_23" : (_GPIO2, 23,         'lcd_hsync'),
  "GPIO2_24" : (_GPIO2, 24,          'lcd_pclk'),
  "GPIO2_25" : (_GPIO2, 25,    'lcd_ac_bias_en'),
  "GPIO3_19" : (_GPIO3, 19,        'mcasp0_fsr'),
  "GPIO3_21" : (_GPIO3, 21,     'mcasp0_ahclkx')
}

for name, (reg, bit_num, mux_name) in _gpio.items():
    setattr(globals(), name, boneio.GPIO(
        registers,
        reg + _GPIO_DATAIN,
        reg + _GPIO_DATAOUT,
        reg + _GPIO_OE,
        muxer,
        mux_name))

##--- End GPIO config ------##
##############################

##############################
##--- Start ADC config: ----##

_ADC_TSC = 0x44e0d000-MMAP_OFFSET


## Registers:

#--- ADC_CTRL ---

_ADC_CTRL = _ADC_TSC+0x40

_TSC_ADC_SS_ENABLE = 0x01 
# To enable:
# _setReg(ADC_CTRL, TSC_ADC_SS_ENABLE)
#  This will turn STEPCONFIG write protect back on 
# To keep write protect off:
# _orReg(ADC_CTRL, TSC_ADC_SS_ENABLE)
#----------------

_ADC_CLKDIV = _ADC_TSC+0x4c  # Write desired value-1

#--- ADC_STEPENABLE ---
_ADC_STEPENABLE = _ADC_TSC+0x54

#----------------------

_ADC_IDLECONFIG = ADC_TSC+0x58

#--- ADC STEPCONFIG ---
_ADCSTEPCONFIG = _ADC_TSC+0x64
_ADCSTEPDELAY  = _ADC_TSC+0x68


_ADC_RESET = 0x00 # Default value of STEPCONFIG

_ADC_AVG2  = 0x01<<2
_ADC_AVG4  = 0x02<<2
_ADC_AVG8  = 0x03<<2
_ADC_AVG16 = 0x04<<2

_SAMPLE_DELAY = lambda cycles: (cycles&0xff)<<24
# SAMPLE_DELAY is the number of cycles to sample for
# Set delay with _orReg(ADCSTEPDELAYx, SAMPLE_DELAY(cycles))

#----------------------

#--- ADC FIFO ---
_ADC_FIFO0DATA = ADC_TSC+0x100

_ADC_FIFO_MASK = 0xfff
# ADC result = _getReg(ADC_FIFO0DATA)&ADC_FIFO_MASK
#----------------

class BeagleboneAnalogInput(boneio.AnalogInput):
    def __init__(self, *args, **kwargs):
        self._cleanup = True
        super(BeagleboneAnalogInput, self).__init__(*args, **kwargs)

    def __del__(self):
        if self._cleanup:
            # Disable ADC subsystem:
            self.registers[_ADC_CTRL] &= ~_TSC_ADC_SS_ENABLE
            # Disable ADC module clock:
            self.registers[_CM_WKUP_ADC_TSC_CLKCTRL] &= ~_MODULEMODE_ENABLE
    
    def _ADCInit(self):
        """ Initializes the on-board 8ch 12bit ADC. """
        # Enable ADC module clock:
        self.registers[_CM_WKUP_ADC_TSC_CLKCTRL] = _MODULEMODE_ENABLE
        # Wait for enable complete:
        while(self.registers[_CM_WKUP_ADC_TSC_CLKCTRL] & _IDLEST_MASK): pass
        # Must turn off STEPCONFIG write protect:
        self.registers[_ADC_CTRL] = 1 << 2
        # Set STEPCONFIG1-STEPCONFIG8 to correspond to ADC inputs 0-7:
        for i in range(8):
            config = (self.bit_num << 19) | _ADC_AVG4
            self.registers[_ADCSTEPCONFIG + 8 * self.bit_num] &= config
        # Now we can enable ADC subsystem, re-enabling write protect:
        self.registers[_ADC_CTRL] = _TSC_ADC_SS_ENABLE
        self._cleanup = True
    
    def _ADCEnabled(self):
        return bool(self.registers[_CM_WKUP_ADC_TSC_CLKCTRL] & _IDLEST_MASK)

## ADC pins:

AIN0 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 1)
AIN1 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 2)
AIN2 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 3)
AIN3 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 4)
AIN4 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 5)
AIN5 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 6)
AIN6 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 7)
AIN7 = BeagleboneAnalogInput(registers, _ADC_STEPENABLE,
                             _ADC_FIFO0DATA, _ADC_FIFO_MASK, 8)

##--- End ADC config -------##
##############################

##############################
##--- Start UART config: ---##

# UART ports must be in form: 
#    [port, tx_pinmux_filename, tx_pinmux_mode, 
#           rx_pinmux_filename, rx_pinmux_mode]

UART = {
  'UART1' : ['/dev/ttyO1', 'uart1_txd', 0,  'uart1_rxd', 0],
  'UART2' : ['/dev/ttyO2',   'spi0_d0', 1,  'spi0_sclk', 1],
  'UART4' : ['/dev/ttyO4',  'gpmc_wpn', 6, 'gpmc_wait0', 6],
  'UART5' : ['/dev/ttyO5', 'lcd_data8', 4,  'lcd_data9', 4]
}

# Formatting constants to mimic Arduino's serial.print() formatting:
DEC = 'DEC'
BIN = 'BIN'
OCT = 'OCT'
HEX = 'HEX'

##--- End UART config ------##
##############################
