from nmigen import *
from nmigen.cli import main

class Spi(Elaboratable):
    '''Basic Spi Module.'''
    def __init__(self, width=8):
        self.ss = Signal()  # FIXME make reset inverted?
        self.mosi = mosi = Signal()
        self.miso = miso = Signal()
        self.in_reg = Signal(width)
        self.in_reg_ready = Signal()

    def elaborate(self, platform):
        m = Module()
        m.domains.spi = ClockDomain()
        bit_count = Signal(max=len(self.in_reg))

        with m.If(~self.ss):
            m.d.spi += bit_count.eq(bit_count + 1)  # Auto wrap around, right?
            with m.If(bit_count == (2**(len(bit_count)) - 1)):  # FIXME better way to do this?
                # Reader of in_reg is expected to clear in_reg_ready after
                # they've read the value from in_reg.
                m.d.spi += self.in_reg_ready.eq(1)
            m.d.spi += self.in_reg.eq(Cat(self.mosi, self.in_reg[:-1]))
        with m.Else():
            # ss is high, so we should just reset everything. FIXME try to
            # re-use built-in reset to achieve this? which would automatically
            # propogate to our submodules (right?)
            m.d.spi += self.in_reg.eq(0)
            m.d.spi += self.in_reg_ready.eq(0)
            m.d.spi += bit_count.eq(0)
        return m

if __name__ == '__main__':
    spi = Spi(8)
    main(spi, ports=[spi.ss, spi.mosi, spi.miso, spi.in_reg, spi.in_reg_ready])
