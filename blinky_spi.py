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

    def elaborate(self, platform):
        m = Module()
        m.submodules.spi = spi = Spi()
        spi_data_in = Signal.like(spi.in_reg)
        spi_data_ready = Signal.like(spi.in_reg_ready)
        m.submodules += MultiReg(Cat(spi.in_reg, spi.in_reg_ready), Cat(spi_data_in, spi_data_ready))

        blink_rate = Signal.like(spi_data_in)  # The value received from SPI
        counter = Signal.like(spi_data_in)  # Sweeping counter used to compare to blink_rate

        # Update blink rate from spi_data
        with m.If(spi_data_ready == 1):
            m.d.sync += blink_rate.eq(spi_data_in)

        m.d.sync += counter.eq(counter + 1)

        with m.If(counter == blink_rate):
            m.d.sync += self.blink_out.eq(1)
        with m.Else():
            with m.If(counter == 0):
                m.d.sync += self.blink_out.eq(0)

        return m

if __name__ == '__main__':
  blinky_spi = BlinkySpi()
  main(blinky_spi, ports=[blinky_spi.ss, blinky_spi.mosi, blinky_spi.blink_out])
