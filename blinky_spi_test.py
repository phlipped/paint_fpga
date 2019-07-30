from migen import *
from testing.testing import READ, WRITE, N, RunTest

from blinky_spi import BlinkySpi

test1 = [
  # clk, ss, mosi, blink
  [0, 0, 0, N], # Pull Slave Select low to activate

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 0, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 1, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 1, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 0, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 0, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 0, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, 0, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, N, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, N, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],

  [1, N, N, N], [1, N, N, N], [1, N, N, N], [1, N, N, N],
  [0, N, N, N], [0, N, N, N], [0, N, N, N], [0, N, N, N],


]

if __name__ == "__main__":
  spi_clk = Signal()
  ss = Signal()
  mosi = Signal()
  blink_out = Signal()

  dut = BlinkySpi(spi_clk, ss, mosi, blink_out)
  pads = [(spi_clk, WRITE), (ss, WRITE), (mosi, WRITE), (blink_out, READ)]
  run_simulation(dut, RunTest(dut, pads, test1, sys_clk_per_iter=4), vcd_name="blinky_spi_sim.vcd")
