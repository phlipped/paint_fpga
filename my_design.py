from migen import *
from spi import Spi
from spi2 import Spi as Spi2

class UsesSpi(Module):
  def __init__(self):
    spi = Spi()
    self.submodules.spi = spi



if __name__ == "__main__":
  #spi = Spi(spi_clk, miso, mosi, ss, data_in_ready, data_in)
  #spi = Spi2()

  from migen.fhdl.verilog import convert
  #convert(spi, ios={miso, mosi, ss, data_in_ready, data_in}).write("my_design_ios.v")
  uses_spi = UsesSpi()
  convert(uses_spi, ios={uses_spi.spi.mosi, uses_spi.spi.miso, uses_spi.spi.spi_clk}).write("my_design_ios.v")
