from migen import *
from testing.testing import READ, WRITE, N, RunTest

from spi import Spi

test1 = [
    # spi_clk, ss, mosi, data_in, data_in_ready
    [N, 1, N, N, N],
    [N, 0, N, N, N], # Slave select goes 0 - we are active now ...
    [0, N, 1, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], #  5
    [0, N, 0, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], #  9
    [0, N, 1, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], # 13
    [0, N, 0, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], # 17
    [0, N, 0, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], # 21
    [0, N, 1, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], # 25
    [0, N, 1, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], # 29
    [0, N, 0, N, 0], [N, N, N, N, 0], [1, N, N, 0xA6, 1], [N, N, N, 0xA6, 1], # 33
    [0, 1, N, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0], # 37
    [0, N, N, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0],
    [0, N, N, N, 0], [N, N, N, N, 0], [1, N, N, N, 0], [N, N, N, N, 0],
]


if __name__  == "__main__":
  spi_clk = Signal()
  ss = Signal()
  mosi = Signal()
  miso = Signal()
  data_in = Signal(8)
  data_in_ready = Signal()

  dut = Spi(spi_clk, ss, mosi, miso, data_in, data_in_ready)
  pads = [(spi_clk, WRITE), (ss, WRITE), (mosi, WRITE), (data_in, READ), (data_in_ready, READ)]
  run_simulation(dut, RunTest(dut, pads, test1, sys_clk_per_iter=5), vcd_name="spi_sim.vcd")

