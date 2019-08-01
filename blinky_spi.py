from migen import *
from spi import Spi
from migen.fhdl import verilog

class BlinkySpi(Module):
  '''Blinky Module that can be programmed by Spi.
  '''
  def __init__(self, spi_clk, ss, mosi, blink_out):
    self.spi_clk = spi_clk
    self.ss = ss
    self.mosi = mosi
    self.blink_out = blink_out

    #########################

    self.spi_data = spi_data = Signal(8)
    self.spi_data_ready = spi_data_ready = Signal()
    self.blink_rate = blink_rate = Signal(8)
    self.counter = counter = Signal(8)

    self.submodules.spi = Spi(spi_clk, ss, mosi, None, spi_data, spi_data_ready)

    # Update blink rate from spi_data
    self.sync += (If(spi_data_ready == 1,
                     blink_rate.eq(spi_data)),
                  counter.eq(counter + 1),
                  If(counter == blink_rate,
                     blink_out.eq(1)),
                  If(counter == 0,
                     blink_out.eq(0)))


if __name__ == '__main__':
  spi_clk = Signal(name='PIN_1')
  ss = Signal(name='PIN_2')
  mosi = Signal(name='PIN_3')
  blink_out = Signal(name='LED')

  blinky = BlinkySpi(spi_clk, ss, mosi, blink_out)

  print(verilog.convert(blinky, {spi_clk, ss, mosi, blink_out}))
