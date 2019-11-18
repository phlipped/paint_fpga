from nmigen import *
from nmigen.cli import main

class Spi(Elaboratable):
    '''Basic Spi Module.'''
    def __init__(self, width=8):
        self.spi_clk_src = Signal()
        self.ss = Signal()  # FIXME make reset inverted?
        self.mosi = mosi = Signal()
        self.miso = miso = Signal()
        self.in_reg = Signal(width)
        self.in_reg_ready = Signal()

    def elaborate(self, platform):
        m = Module()
        m.d.domains.sync = ClockDomain()
        m.d.domains.spi = ClockDomain()

        # Drive the spi_domain clock using the aligned spi clock
        m.d.comb += m.d.spi.clk.eq(self.spi_clk_src)

        bit_count = Signal(max=len(self.in_reg))

        with m.If(~self.ss):
            # Increment counter
            m.d.spi += bit_count.eq(bit_count + 1)

            # When counter is at max
            with m.If(bit_count == (2**(len(bit_count)) - 1)):
                m.d.spi += (self.in_reg_ready.eq(1))
            with m.Else():
                m.d.spi += self.in_reg_ready.eq(0)

            # Shift data into in_reg
            m.d.spi += self.in_reg.eq(Cat(self.mosi, self.in_reg[:-1]))
        with m.Else():
            # ss is high, so reset
            # FIXME try to re-use built-in reset to achieve this?
            m.d.spi += (self.in_reg.eq(0),
                        self.in_reg_ready.eq(0),
                        bit_count.eq(0))
        return m

if __name__ == '__main__':
    spi = Spi(8)
    main(spi, ports=[spi.ss, spi.mosi, spi.miso, spi.in_reg, spi.in_reg_ready])
