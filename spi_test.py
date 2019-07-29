from migen import *

from spi import Spi

if __name__  == "__main__":
  ss = Signal()
  spi_clk = Signal()
  miso = Signal()
  mosi = Signal()
  data_in = Signal(8)
  data_in_ready = Signal()

  dut = Spi(spi_clk, ss, miso, mosi, data_in, data_in_ready)
  # run_simulation(dut, test(dut.spi_clk, dut.ss, dut.miso, dut.mosi), vcd_name="spi_sim.vcd")

