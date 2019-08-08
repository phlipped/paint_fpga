from nmigen import *
from nmigen.cli import main
from edge_detect import EdgeDetect

class Spi(Module):
    '''Basic Spi Module.'''
    def __init__(self, width=8):
        self.spi_clk = Signal()
        self.ss = Signal()  # FIXME make reset inverted?
        self.mosi = mosi = Signal()
        self.miso = miso = Signal()
        self.in_reg = Signal(width)
        self.in_reg_ready = Signal()

    def elaborate(self, platform):
        m = Module()

        m.submodules.spi_edge = spi_edge = EdgeDetect(rising = True)
        spi_edge.sig = self.spi_clk

        spi_clk_rising = spi_edge.rising
        bit_count = Signal(max=len(self.in_reg))

        with m.If(~self.ss):
            with m.If(spi_clk_rising):
                m.d.sync += bit_count.eq(bit_count + 1),  # Auto wrap around, right?
                with m.If(bit_count == len(self.in_reg) - 1):  # FIXME better to check if bit_count is at it's own max value? just not sure how to do that
                    # Reader of in_reg is expected to clear data_in_ready after
                    # they've read the value from in_reg.
                    m.d.sync += self.in_reg_ready.eq(1)
                m.d.sync += self.in_reg.eq(Cat(self.mosi, self.in_reg[:-1]))
        with m.Else():
            # ss is high, so we should just reset everything. FIXME try to
            # re-use built-in reset to achieve this? which would automatically
            # propogate to our submodules (right?) FIXME reset our edge_detect
            # module
            m.d.sync += self.in_reg.eq(0)
            m.d.sync += self.in_reg_ready.eq(0)
            m.d.sync += bit_count.eq(0)
        return m

if __name__ == '__main__':
    spi = Spi(8)
    main(spi, ports=[spi.spi_clk, spi.ss, spi.mosi, spi.miso, spi.in_reg, spi.in_reg_ready])
