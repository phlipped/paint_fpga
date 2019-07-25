from migen import *

from spi import EdgeDetect, Spi

SPI_CLK_RATIO = 100

class TestPads():
  def __init__(self):
    self.miso = Signal()
    self.mosi = Signal()
    self.ss = Signal(reset = 1)
    self.spi_clk = Signal()

def _pulse_spi_clk(spi_clk):
  yield spi_clk.eq(1)
  for i in range(SPI_CLK_RATIO):
    yield
  yield spi_clk.eq(0)
  for i in range(SPI_CLK_RATIO):
    yield

def _test2(pads):
  yield
  yield from _pulse_spi_clk(pads.spi_clk)
  yield pads.ss.eq(0)
  yield from _pulse_spi_clk(pads.spi_clk)
  yield pads.mosi.eq(1)
  yield from _pulse_spi_clk(pads.spi_clk)
  yield from _pulse_spi_clk(pads.spi_clk)
  yield pads.mosi.eq(0)
  yield from _pulse_spi_clk(pads.spi_clk)
  yield from _pulse_spi_clk(pads.spi_clk)
  yield pads.ss.eq(1)
  yield from _pulse_spi_clk(pads.spi_clk)


def _test(spi_clk, ss, miso, mosi):
  yield ss.eq(1)
  yield from _pulse_spi_clk(spi_clk)
  yield from _pulse_spi_clk(spi_clk)
  yield ss.eq(0)
  yield from _pulse_spi_clk(spi_clk)
  yield mosi.eq(1)
  yield from _pulse_spi_clk(spi_clk)
  yield mosi.eq(0)
  yield from _pulse_spi_clk(spi_clk)
  yield mosi.eq(1)
  yield from _pulse_spi_clk(spi_clk)

if __name__  == "__main__":
  dut = Spi()
  run_simulation(dut, _test(dut.spi_clk, dut.ss, dut.miso, dut.mosi), vcd_name="spi_sim.vcd")
