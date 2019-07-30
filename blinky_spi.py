from migen import *
from spi import Spi

class BlinkySpi(Module):
  '''Blinky Module that can be programmed by Spi.
  '''
  def __init__(self, spi_clk, ss, mosi, blink_out):
    spi_data = Signal(8)
    spi_data_ready = Signal()
    blink_rate = Signal(8)
    counter = Signal(8)

    self.submodules.spi = Spi(spi_clk, ss, mosi, None, spi_data, spi_data_ready)

    # Update blink rate from spi_data
    self.sync += (If(spi_data_ready == 1,
                     blink_rate.eq(spi_data)),
                  counter.eq(counter + 8),
                  If(counter == spi_data,
                     blink_out.eq(1)),
                  If(counter == 0,
                     blink_out.eq(0)))

