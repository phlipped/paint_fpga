from migen import *
from edge_detect import EdgeDetect

class Spi(Module):
  '''Basic Spi Module.

  Signal Args:
    spi_clk: Signal 1 x in
    ss: Signal 1 x in
    miso: Signal 1 x out
    mosi: Signal 1 x in
    data_in: Signal n x in/out
    data_in_ready: Signal 1 x out

  Not Yet implemented:
    miso: Signal 1 x out
    data_out: Signal n x out
    data_out_ready: Signal 1 x out
  '''
  def __init__(self, spi_clk, ss, miso, mosi, data_in, data_in_ready):
    self.spi_clk = spi_clk
    self.ss = ss
    self.miso = miso
    self.mosi = mosi
    self.data_in = data_in
    self.data_in_ready = data_in_ready
    # self.data_out = data_out = Signal(word_size)  # FIXME

    ###

    rising = Signal()
    self.submodules.spi_edge = EdgeDetect(spi_clk, rising)

