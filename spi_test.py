from migen import *

from spi import Spi

if __name__  == "__main__":
  dut = Spi()
  run_simulation(dut, _test(dut.spi_clk, dut.ss, dut.miso, dut.mosi), vcd_name="spi_sim.vcd")

