'''Implements a counter driven by an external clock'''

from nmigen import *
from nmigen.cli import main

class ExtCounter(Elaboratable):
  def __init__(self):
    self.count = Signal(22)

  def elaborate(self, platform):
    ext_clock = platform.request('ext_clock')

    m = Module()
    m.domains.ext = ClockDomain('ext')

    m.d.ext += self.count.eq(self.count + 1)
    m.d.comb += ClockSignal('ext').eq(ext_clock)
    return m

if __name__ == '__main__':
  ext_counter = ExtCounter()
  main(ext_counter)
