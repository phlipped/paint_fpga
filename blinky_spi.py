from nmigen import *
from spi import Spi
from nmigen.cli import main


class BlinkySpi(Elaboratable):
    '''Blinky Module that can be programmed by Spi.'''
    def __init__(self):
        self.spi = Spi()
        self.blink_out = Signal()

    def elaborate(self, platform):
        m = Module()

        m.submodules.spi = self.spi

        blink_rate = Signal(self.spi.in_reg.shape())
        counter = Signal(self.spi.in_reg.shape())  # Sweeping counter used to compare to blink_rate

        # Update blink rate from spi_data
        with m.If(self.spi.in_reg_ready == 1):
            m.d.sync += blink_rate.eq(self.spi.in_reg)

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
  main(blinky_spi, ports=[blinky_spi.spi.spi_clk, blinky_spi.spi.ss, blinky_spi.spi.mosi, blinky_spi.blink_out])
