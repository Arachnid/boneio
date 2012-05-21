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
CM_WKUP = 0x44e00400-MMAP_OFFSET

CM_WKUP_ADC_TSC_CLKCTRL = 0xbc+CM_WKUP

MODULEMODE_ENABLE = 0x02
IDLEST_MASK = 0x03<<16
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

ADC_TSC = 0x44e0d000-MMAP_OFFSET

## Registers:

#--- ADC_CTRL ---
ADC_CTRL = ADC_TSC+0x40

ADC_STEPCONFIG_WRITE_PROTECT = lambda state: (state^0x01)<<2
# Write protect default on, must first turn off to change stepconfig:
# _setReg(ADC_CTRL, ADC_STEPCONFIG_WRITE_PROTECT(0))
 
TSC_ADC_SS_ENABLE = 0x01 
# To enable:
# _setReg(ADC_CTRL, TSC_ADC_SS_ENABLE)
#  This will turn STEPCONFIG write protect back on 
# To keep write protect off:
# _orReg(ADC_CTRL, TSC_ADC_SS_ENABLE)
#----------------

ADC_CLKDIV = ADC_TSC+0x4c  # Write desired value-1

#--- ADC_STEPENABLE ---
ADC_STEPENABLE = ADC_TSC+0x54

ADC_ENABLE = lambda AINx: 0x01<<(ADC[AINx]+1)
#----------------------

ADC_IDLECONFIG = ADC_TSC+0x58

#--- ADC STEPCONFIG ---
ADCSTEPCONFIG1 = ADC_TSC+0x64
ADCSTEPDELAY1  = ADC_TSC+0x68
ADCSTEPCONFIG2 = ADC_TSC+0x6c
ADCSTEPDELAY2  = ADC_TSC+0x70
ADCSTEPCONFIG3 = ADC_TSC+0x74
ADCSTEPDELAY3  = ADC_TSC+0x78
ADCSTEPCONFIG4 = ADC_TSC+0x7c
ADCSTEPDELAY4  = ADC_TSC+0x80
ADCSTEPCONFIG5 = ADC_TSC+0x84
ADCSTEPDELAY5  = ADC_TSC+0x88
ADCSTEPCONFIG6 = ADC_TSC+0x8c
ADCSTEPDELAY6  = ADC_TSC+0x90
ADCSTEPCONFIG7 = ADC_TSC+0x94
ADCSTEPDELAY7  = ADC_TSC+0x98
ADCSTEPCONFIG8 = ADC_TSC+0x9c
ADCSTEPDELAY8  = ADC_TSC+0xa0
# Only need the first 8 steps - 1 for each AIN pin


ADC_RESET = 0x00 # Default value of STEPCONFIG

ADC_AVG2  = 0x01<<2
ADC_AVG4  = 0x02<<2
ADC_AVG8  = 0x03<<2
ADC_AVG16 = 0x04<<2

SEL_INP = lambda AINx: (ADC[AINx]+1)<<19
# Set input with _orReg(ADCSTEPCONFIGx, SEL_INP(AINx))
# ADC[AINx]+1 because positive AMUX input 0 is VREFN 
#  (see user manual section 12.3.7)

SAMPLE_DELAY = lambda cycles: (cycles&0xff)<<24
# SAMPLE_DELAY is the number of cycles to sample for
# Set delay with _orReg(ADCSTEPDELAYx, SAMPLE_DELAY(cycles))

#----------------------

#--- ADC FIFO ---
ADC_FIFO0DATA = ADC_TSC+0x100

ADC_FIFO_MASK = 0xfff
# ADC result = _getReg(ADC_FIFO0DATA)&ADC_FIFO_MASK
#----------------

## ADC pins:

ADC = {
  'AIN0' : 0x00,
  'AIN1' : 0x01,
  'AIN2' : 0x02,
  'AIN3' : 0x03,
  'AIN4' : 0x04,
  'AIN5' : 0x05,
  'AIN6' : 0x06,
  'AIN7' : 0x07,
  'VSYS' : 0x07
}
# And some constants so the user doesn't need to use strings:
AIN0 = A0 = 'AIN0'
AIN1 = A1 = 'AIN1'
AIN2 = A2 = 'AIN2'
AIN3 = A3 = 'AIN3'
AIN4 = A4 = 'AIN4'
AIN5 = A5 = 'AIN5'
AIN6 = A6 = 'AIN6'
AIN7 = A7 = VSYS = 'AIN7'

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
