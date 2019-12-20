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

        New data for sending can be asserted on o_reg at any time - but it will
        only be copied to an internal buffer in the same cycle that out_count
        changes from non-zero to zero. In other words, the next value to be
        sent out to miso will be whatever value was present on o_reg
        immediately prior to out_count becoming zero.

        Also, none of this factors in an SS reset, which is something that
        needs to be worked on.
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

class SpiRegIf(Elaboratable):
    '''
    Args:
      regs: a dictionary of {integer: (Signal(), bool)}, where integer is the
      'address' that will be used in SPI commands. The bool indicates whether
      the register is writable from SPI. All registers are readable.

      Writable registers must not be driven by any other processes
    '''
    def __init__(self, regs):
        self.spi_width = self._check_regs(regs)
        self.spi_clk = Signal()
        self.ss = Signal()
        self.mosi = Signal()
        self.miso = Signal()
        # FIXME create relevant structures here?

    def _check_regs(self, regs):
        width = None
        for addr, (sig, rw) in regs.items():
            if width is None:
                width = len(sig)
            if not isinstance(width, int):
                raise Exception("bad type for addr - should be int, but found {!r}".format(addr))
            if not isinstance(rw, bool):
                raise Exception("bad type for rw - should be bool, but found {!r}".format(rw))
            if len(sig) != width:
                raise Exception("bad regs - Signal for addr {} has different width - {} instead of {}".format(addr, len(sig), width))
        return width

    def elaborate(self, platform):
        m = Module()

        spi_core = SpiCore(self.width)
        spi_core.spi_clk = self.spi_clk
        spi_core.ss = self.ss
        spi_core.mosi = self.mosi
        spi_core.miso = self.miso
        m.submodules += spi_core

        self.status = Signal()

        with m.FSM() as fsm:            
            with m.State("START"):
                pass

            with m.State("WAITING"):
                # just waiting for Spi Core slave select to go low
                pass

            with m.State("GET_CMD"):
                pass

            with m.State("HANDLE_WRITE"):
                '''
                ok, so let's assume there is a register somewhere that has an address in it
                and let's assume we went ahead and received the value we need to write.
                How do we use the passed in addr to select the appropriate register?

                '''
                pass

            with m.State("HANDLE_READ"):
                pass

            with m.State("ERROR"):
                pass

        return m
