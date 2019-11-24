from nmigen import *

class ShiftRegister(Elaboratable):
    '''Just a shift register, with both input and output signals.

    TODO: Not sure what happens if the input or output isn't used - do they
    get optimized out? Hopefully they do.
    '''
    def __init__(self, depth):
        self.i = Signal()
        self.o = Signal()
        self.reg = Signal(depth)

    def elaborate(self, platform):
        m = Module()

        # Pair up each bit of reg with it's neighbor - with self.i going to the
        # first bit, and the last bit going to self.o
        shifted_pairs = zip((self.i, *self.reg), (*self.reg, self.o))
        m.d.sync += [o.eq(i) for i, o in shifted_pairs]

        return m
