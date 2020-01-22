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
        self._o_reg = Signal(self.o_reg.width)
        self.count = Signal(range(0, width))  # counts number of bits sent/received
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

            # increment count, wrapping as necessary
            with m.If(self.count == self.i_reg.width - 1): # if: count was 1 less than i_reg width
                                                              #     then we just received the last bit, so ...
                m.d.spi_rising += [
                    self.read_ready.eq(1),                    #     set read_ready
                    self.count.eq(0),                      #     reset count to 0
                ]
            with m.Else():                                    # else: we aren't at the last bit
                m.d.spi_rising += [
                    self.read_ready.eq(0),                    #     so ensure read_ready is 0
                    self.count.eq(self.count + 1)       #     and increment count
                ]


            # bind miso to the last bit of _o_reg
            m.d.comb += self.miso.eq(self._o_reg[-1])

            with m.If(self.count == 0):
                m.d.spi_falling += [
                    self._o_reg.eq(self.o_reg),
                ]
            with m.Else():
                m.d.spi_falling += [o.eq(i) for i, o in zip((0, *self._o_reg), self._o_reg)]
        return m

class SpiRegIf(Elaboratable):
    '''
    Args:
      read_regs: an indexable collection of Signals. Addresses (0 indexed) are assigned to the registers
      in the order they appear in the list.

      write_regs: an indexable collection of Signals. Addresses (0 indexed) are assigned to the registers
      in the order they appear in the list. The same register can be present in read_regs and write_regs.
      The addressing domain of each collection is separate - address 0 in read_regs is different to
      address 0 in write_regs, although you can arrange for a single address to identify the same
      register by adding the register in the same index in each list.

      Writable registers cannot be driven by any other modules - SpiRegIf module
      takes ownership of setting the value in these registers.
    '''
    def __init__(self, read_regs, write_regs):
        if read_regs[0].shape().width != write_regs[0].shape().width:
            raise Exception("size of registers in read_regs must be the same as in write_regs")
        self.spi_width = read_regs[0].shape().width
        self.spi_clk = Signal()
        self.ss = Signal()
        self.mosi = Signal()
        self.miso = Signal()
        self.read_regs = read_regs
        self.write_regs = write_regs

        self.addr = Signal(self.spi_width)

    def elaborate(self, platform):
        m = Module()

        spi_core = SpiCore(self.spi_width)
        spi_core.spi_clk = self.spi_clk
        spi_core.ss = self.ss
        spi_core.mosi = self.mosi
        spi_core.miso = self.miso
        m.submodules += spi_core

        # nmigen simulator bug
        #self.spi_clk2 = Signal()
        #self.ss2 = Signal()
        #self.mosi2 = Signal()
        #self.read_regs2 = Array([Signal(len(r)) for r in self.read_regs])
        #self.write_regs2 = Array([Signal(len(r)) for r in self.write_regs])
        #m.d.comb += [
        #    self.spi_clk2.eq(self.spi_clk),
        #    self.ss2.eq(self.ss),
        #    self.mosi2.eq(self.mosi),
        #]
        #m.d.comb += [o.eq(i) for i, o in zip(self.read_regs, self.read_regs2)]
        #m.d.comb += [o.eq(i) for i, o in zip(self.write_regs, self.write_regs2)]

        with m.FSM() as fsm:
            with m.State("START"):
                m.next = "WAIT_FOR_CMD"

            with m.State("WAIT_FOR_CMD"):
                # just waiting for Spi Core to have some data
                with m.If(spi_core.read_ready == 1):
                    # Store the remaining bits of i_reg in addr
                    # The MSB indicates read or write, so we remove it and
                    # replace it with a zero
                    m.d.sync += self.addr.eq(spi_core.i_reg & 0b01111111)
                    with m.If(spi_core.i_reg[-1] == 0):
                        m.next = "HANDLE_READ"
                    with m.Else():
                        m.next = "HANDLE_WRITE"

            with m.State("HANDLE_WRITE"):
                # We need to wait for the previous value to go away
                with m.If(spi_core.read_ready == 0):
                    m.next = "HANDLE_WRITE_1"

            with m.State("HANDLE_WRITE_1"):
                # Now wait for a new value to be ready
                with m.If(spi_core.read_ready == 1):
                    # FIXME don't write into read-only regs
                    # Might need a separate array of single digit regs that
                    # correspond to each reg in the main regs array?
                    m.d.sync += self.write_regs[self.addr].eq(spi_core.i_reg)
                    m.next = "HANDLE_WRITE_2"

            with m.State("HANDLE_WRITE_2"):
                # Wait for the data to be gone, and then go back to state "WAIT_CMD_READY"
                with m.If(spi_core.read_ready == 0):
                    m.next = "WAIT_FOR_CMD"

            with m.State("HANDLE_READ"):
                m.d.sync += spi_core.o_reg.eq(self.read_regs[self.addr])
                m.next = "HANDLE_READ_1"

            with m.State("HANDLE_READ_1"):
                with m.If(spi_core.read_ready == 0):
                    m.next = "WAIT_FOR_CMD"

            with m.State("ERROR"):
                pass

        return m
