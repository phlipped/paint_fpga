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
        in_buf = Signal.like(self.in_reg)
        bit_count = Signal(max=len(in_buf))

        with m.If(~self.ss):
            m.d.spi += bit_count.eq(bit_count + 1)  # Auto wraps around, right?
            with m.If(bit_count == (2**(len(bit_count)) - 1)):
                m.d.spi += (self.in_reg_ready.eq(1),
                            self.in_reg.eq(in_buf))
            with m.Else():
                m.d.spi += self.in_reg_ready.eq(0)
            m.d.spi += in_buf.eq(Cat(self.mosi, in_buf[:-1]))
        with m.Else():
            # ss is high, so we should just reset everything.
            # FIXME try to re-use built-in reset to achieve this?
            m.d.spi += (in_buf.eq(0),
                        self.in_reg.eq(0),
                        self.in_reg_ready.eq(0),
                        bit_count.eq(0))
        return m

if __name__ == '__main__':
    spi = Spi(8)
    main(spi, ports=[spi.ss, spi.mosi, spi.miso, spi.in_reg, spi.in_reg_ready])
