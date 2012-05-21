import mmap

class RegisterMap(object):
    def __init__(self, start_address, end_address=None, length=None, register_size=32):
        if register_size not in (16, 32):
            raise ValueError("Invalid register length: %i - must be 16 or 32" % self.map.register_size)
        self.register_size = register_size

        self.start_address = start_address
        if length:
            self.length = length
        else:
            self.length = end_address - start_address
        self.fh = open("/dev/mem", "r+b")
        self.mem = mmap.mmap(self.fh.fileno(), length, offset=start_address)

    def __getitem__(self, address):
        """ Returns unpacked 16 or 32 bit register value starting from address. """
        if (self.register_size == 32):
          return struct.unpack("<L", self.map.mem[address:address+4])[0]
        elif (self.register_size == 16):
          return struct.unpack("<H", self.map.mem[address:address+2])[0]

    def __setitem__(self, address, val):
        """ Sets 16 or 32 bits at given address to given value. """
        if (self.register_size == 32):
          __mmap[address:address+4] = struct.pack("<L", val)
        elif (self.register_size == 16):
          __mmap[address:address+2] = struct.pack("<H", val)

    def close(self):
        self.mem.close()
        self.fh.close()

    def __del__(self):
        self.close()


class Muxer(object):
    PULLUP = None
    PULL_DISABLE = None
    GPIO_INPUT = None
    GPIO_OUTPUT = None

    def __init__(self, base_path):
        self.base_path = base_path

    def mux(self, pin, mode):
        """ Uses kernel omap_mux files to set pin modes. """
        # There's no simple way to write the control module registers from a 
        # user-level process because it lacks the proper privileges, but it's 
        # easy enough to just use the built-in file-based system and let the 
        # kernel do the work. 
        with open(self.base_path + pin, 'wb') as f:
            f.write('%x' % mode) # Write hex string (stripping off '0x')

    def gpio_in(self, pin, pull=0):
        mode = self.GPIO_INPUT
        if pull > 0:
            mode |= self.PULLUP
        elif pull == 0:
            mode |= self.PULL_DISABLE
        self.mux(pin, mode)

    def gpio_out(self, pin):
        self.mux(pin, self.GPIO_OUTPUT)


class GPIO(object):
    def __init__(self, registers, in_reg, out_reg, dir_reg, bit_num, muxer, mux_name):
        self.registers = registers
        self.in_reg = in_reg
        self.out_reg = out_reg
        self.dir_reg = dir_reg
        self.bit_num = bit_num
        self.muxer = muxer
        self.mux_name = mux_name

    def output(self):
        """Sets GPIO to output mode."""
        self.muxer.gpio_out(self.mux_name)
        self.registers[self.dir_reg] &= ~(1 << self.bit_num)
    
    def input(self, pull=0):
        """Sets GPIO to input mode."""
        self.muxer_gpio_in(self.mux_name, pull)
        self.registers[self.dir_reg] |= 1 << self.bit_num
    
    @property
    def value(self):
        """Gets/sets the current value of the GPIO pin."""
        return (self.registers[self.in_reg] >> self.bit_num) & 0x1

    @value.setter
    def value(self, val):
        if val:
            self.set()
        else:
            self.clear()

    @property
    def state(self):
        """The current state of the pin if configured as an output."""
        if self.registers[self.dir_reg] & (1 << self.bit_num):
            return None
        return (self.registers[self.dir_reg] >> self.bit_num) & 0x1

    def set(self):
        """Sets the pin output to high."""
        self.registers[self.out_reg] |= 1 << self.bit_num

    def clear(self):
        """Sets the pin output to low."""
        self.registers[self.out_reg] &= ~(1 << self.bit_num)

    def toggle(self):
        """Toggles the value of the output pin."""
        if self.value:
            self.clear()
        else:
            self.set()
