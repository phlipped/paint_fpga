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
    '''Shift register that asserts a Data Ready flag when data is ready to read.

    Normal use case is for serial to parallel conversion.

    It basically does this by counting the incoming bits and asserting data
    ready whenever there is a full buffer-width's worth of bits.

    data_ready is asserted combinatorially based on the comparison of an
    internal counter to the width of the register
    '''
    def __init__(self, width):
        super(ShiftRegisterWithDataReady, self).__init__(width)
        self.data_ready = Signal()
        self.count = Signal(range(0, len(self.reg)))

    def elaborate(self, platform):
        m = super(ShiftRegisterWithDataReady, self).elaborate(platform)

        with m.If(self.count == len(self.reg)):
            m.d.sync += [self.count.eq(1),
                         self.data_ready.eq(1),]
        with m.Else():
            m.d.sync += [self.count.eq(self.count + 1),
                         self.data_ready.eq(0),]

        return m

class SpiCore(Elaboratable):
    def __init__(self, width):
        '''Core SPI logic for shifting data in and out.

        This module deals only with basic logic of moving the bits around - it
        explicitly does NOT want to worry about clock domains. As such, all
        SPI input signals (clk, ss and mosi) should be synchronised to the
        'sync' clock domain.

        spi_clk is used to drive the shift registers at the core of this module.

        Data is read on the rising edge, and sent on the falling edge.

        When a full word of data has been read, read_ready will be set to 1 for
        the duration of one spi_clk cycle.

        When a full word of data has been sent, send_ready will be set to 1 for
        the duration of one spi_clk cycle.

        New data for sending can be written to o_reg at any time, but it will
        only be copied to the underlying output buffer and shifted out to miso
        when the previous data has finished being sent out.
        '''
        self.spi_clk = Signal() # read only
        self.ss = Signal(reset=1) # read only, active low
        self.mosi = Signal() # read only
        self.miso = Signal() # should be wired directly to GPIO output

        self.i_reg = Signal(width)
        self.o_reg = Signal(width)
        self.in_count = Signal(range(0, width-1))
        self.out_count = Signal(range(0, width-1))
        self.read_ready = Signal()

        # internal only - added here to expose to testing
        self._o_reg = Signal(self.o_reg.width)

    def elaborate(self, platform):
        m = Module()

        # Create edge detect module
        m.submodules.spi_edges = spi_edges = EdgeDetect()
        spi_edges.i = self.spi_clk

        # Everything happens when self.ss is low (active)
        with m.If(self.ss == 0):

            # Update recv/send shift registers, update counts, update ready flags
            with m.If(spi_edges.rising == 1):
                # shift from mosi into i_reg
                m.d.sync += [o.eq(i) for i, o in zip((self.mosi, *self.i_reg), self.i_reg)]

                # increment in_count, wrapping as necessary
                with m.If(self.in_count == self.i_reg.width - 1): # if count is currently 1 less than i_reg width
                                                             #    then we just received the last bit, so ...
                    m.d.sync += [self.read_ready.eq(1),        # set read_ready
                                 self.in_count.eq(0)]            # reset in_count to 0
                with m.Else():                               # else we aren't at the last bit
                    m.d.sync += [self.read_ready.eq(0),        # so ensure read_ready is 0
                                 self.in_count.eq(self.in_count + 1)]  # and increment in_count

            # falling edge of spi clock
            with m.If(spi_edges.falling == 1):
                # on falling edge, we always shift out _o_reg
                m.d.sync += [o.eq(i) for i, o in zip((0, *self._o_reg), (*self._o_reg, self.miso))]

                with m.If(self.out_count == self.o_reg.width - 1):
                    m.d.sync += self.out_count.eq(0),          # reset out_count to 0
                with m.Else():
                    m.d.sync += self.out_count.eq(self.out_count + 1)
            with m.Else(): # Not falling edge
                with m.If(self.out_count == 0): # count is 0, so load _o_reg from o_reg
                    m.d.sync += self._o_reg.eq(self.o_reg)

        with m.Else():
            # ss is not active, so we should reset everything
            pass
        return m

class EdgeDetect(Elaboratable):
    def __init__(self, depth=2):
      self.i = Signal()
      self.rising = Signal()
      self.falling = Signal()

      # Not part of the interface, but exposed here to make testing easy
      self.buf = Signal(depth)

    def elaborate(self, platform):
      m = Module()

      m.d.sync += [o.eq(i) for i, o in zip((self.i, *self.buf), (self.buf))]
      with m.If(self.buf[-2:] == 0b10):
        m.d.sync += self.falling.eq(1)
      with m.Else():
        m.d.sync += self.falling.eq(0)

      with m.If(self.buf[-2:] == 0b01):
        m.d.sync += self.rising.eq(1)
      with m.Else():
        m.d.sync += self.rising.eq(0)

      return m
