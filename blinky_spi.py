from nmigen import *
from spi import Spi
from nmigen.cli import main

class BlinkySpi(Elaboratable):
    '''Blinky Module that can be programmed by Spi.
    '''
    def __init__(self):
        self.ss = Signal()
        self.mosi = mosi = Signal()
        self.blink_out = Signal()
        self.spi_clk = Signal()

    def elaborate(self, platform):
        m = Module()

        m.submodules.spi = spi = Spi()

        # Align the external clock signal to the internal clock
        # Assumes that the external clock is much slower than internal clock
        # Use the aligned signal to drive the spi submodule
        spi_clk_aligned = Signal(3)
        m.d.sync += spi_clk_aligned.eq(Cat(self.spi_clk, spi_clk_aligned[:-1]))
        m.d.comb += spi.spi_clk.clk.eq(spi_clk_aligned[-1])

        # Hook up the ss and mosi signals to the spi module
        spi.ss = self.ss
        spi.mosi = self.mosi

        blink_rate = Signal(spi.in_reg.shape())
        counter = Signal(spi.in_reg.shape())  # Sweeping counter used to compare to blink_rate

        # Update blink rate from spi_data
        with m.If(spi.in_reg_ready == 1):
            m.d.sync += blink_rate.eq(spi.in_reg)

        # Increment the counter
        m.d.sync += counter.eq(counter + 1)

        # Compare counter to blink_rate and 0, set blink_out accordingly
        with m.If(counter == blink_rate):
            m.d.sync += self.blink_out.eq(1)
        with m.Else():
            with m.If(counter == 0):
                m.d.sync += self.blink_out.eq(0)

        return m

if __name__ == '__main__':
  blinky_spi = BlinkySpi()
  main(blinky_spi, ports=[blinky_spi.spi_clk, blinky_spi.ss, blinky_spi.mosi, blinky_spi.blink_out])
