import math

from nmigen import *

class ShiftRegister(Elaboratable):
    '''Just a shift register, with both input and output signals.

    TODO: Not sure what happens if the input or output isn't used - do they
    get optimized out? Hopefully they do.
    '''
    def __init__(self, width):
        self.i = Signal()
        self.o = Signal()
        self.reg = Signal(width)

    def elaborate(self, platform):
        m = Module()

        # Pair up each bit of reg with it's neighbor - with self.i going to the
        # first bit, and the last bit going to self.o
        shifted_pairs = zip((self.i, *self.reg), (*self.reg, self.o))
        m.d.sync += [o.eq(i) for i, o in shifted_pairs]

        return m

class ShiftRegisterWithDataReady(ShiftRegister):
    '''Shift register that asserts a Data Ready flag when data is ready.

    It basically does this by counting the incoming bits and asserting data
    ready whenever there is a full buffer-width's worth of bits.

    data_ready is asserted combinatorially based on the comparison of an
    internal counter to the width of the register
    '''
    def __init__(self, width):
        super(ShiftRegisterWithDataReady, self).__init__(width)
        self.data_ready = Signal()

    def elaborate(self, platform):
        m = super(ShiftRegisterWithDataReady, self).elaborate(platform)
        count = Signal(range(0, len(self.reg)))

        with m.If(count == len(self.reg)):
            m.d.sync += count.eq(1)
            m.d.comb += self.data_ready.eq(1)
        with m.Else():
            m.d.sync += count.eq(count + 1)

        return m
