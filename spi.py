from nmigen import *

class SpiCore(Elaboratable):
    def __init__(self, width):
        '''Core SPI logic for shifting data in and out.

        The intention of this module is that it operates in a
        separate-but-synchronised clock domain - ie a clock domain that ticks
        at a different frequency, but changes state at the same time as the main
        sync clock domain of the containing module. As such, although the SPI
        input signals (clk, ss and mosi) are controlled externally, they should
        be synchronised to the main clock before they are passed to this module.

        spi_clk is used to drive the shift registers at the core of this module.

        Data is read from mosi on the rising edge, and sent on miso the falling
        edge of spi_clk

        When a full word of data has been read, read_ready will be set to 1 for
        the duration of one spi_clk cycle.

        New data for sending can be written to o_reg at any time, but it will
        only be copied to the underlying output buffer and shifted out to miso
        after the previous data has finished being sent out. The following
        procedure should be followed:
         - wait for out_count to be non-zero
         - load o_reg with a value
         - wait for out_count to be zero
         - at this point, the data has been accepted into _o_reg and will be
           sent out as the next word on miso
        '''
        self.spi_clk = Signal() # read only
        self.ss = Signal(reset=1) # read only, active low
        self.mosi = Signal() # read only
        self.miso = Signal() # should be wired directly to GPIO output

        self.i_reg = Signal(width)
        self.o_reg = Signal(width)
        self.in_count = Signal(range(0, width))
        self.out_count = Signal(range(0, width))
        self.read_ready = Signal()

    def elaborate(self, platform):
        m = Module()

        # Create an spi clock domain driven by a
        # synchronised-but-externally-controlled spi master clock
        spi_rising = ClockDomain('spi_rising')
        spi_rising.clk = self.spi_clk
        spi_falling = ClockDomain('spi_falling', clk_edge='neg')
        spi_falling.clk = self.spi_clk
        m.domains += spi_rising
        m.domains += spi_falling

        # This is the actual shift register that delivers data to miso
        # It is loaded from o_reg when the last bit of the previous value
        # is shifted out onto the miso line.
        _o_reg = Signal(self.o_reg.width)

        # These are needed to overcome a bug in the nmigen simulator where
        # un-driven signals aren't included in the VCD file.
        # Once the bug is fixed, this lot can be removed.
        # https://github.com/m-labs/nmigen/issues/280
        o_reg2 = Signal(len(self.o_reg))
        ss2 = Signal(reset=1)
        mosi2 = Signal()
        m.d.comb += [ss2.eq(self.ss),
                     mosi2.eq(self.mosi),
                     o_reg2.eq(self.o_reg)]

        # Everything happens when self.ss is low (active)
        with m.If(self.ss == 0):
            # shift from mosi into i_reg
            m.d.spi_rising += [o.eq(i) for i, o in zip((self.mosi, *self.i_reg), self.i_reg)]

            # increment in_count, wrapping as necessary
            with m.If(self.in_count == self.i_reg.width - 1): # if: count is currently 1 less than i_reg width
                                                              #     then we just received the last bit, so ...
                m.d.spi_rising += [self.read_ready.eq(1),     #     set read_ready
                                   self.in_count.eq(0)]       #     reset in_count to 0
            with m.Else():                                    # else: we aren't at the last bit
                m.d.spi_rising += [self.read_ready.eq(0),     #     so ensure read_ready is 0
                                   self.in_count.eq(self.in_count + 1)]  # and increment in_count

            m.d.spi_falling += self.miso.eq(_o_reg[-1])

            with m.If(self.out_count == self.o_reg.width - 1):
                m.d.spi_falling += [self.out_count.eq(0),
                                    _o_reg.eq(self.o_reg)]
            with m.Else():
                m.d.spi_falling += self.out_count.eq(self.out_count + 1)
                m.d.spi_falling += [o.eq(i) for i, o in zip((0, *_o_reg), _o_reg)]
        return m
