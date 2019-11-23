'''Implements a counter driven by an external clock'''

from nmigen import *
from nmigen.lib.cdc import FFSynchronizer
from nmigen.cli import main

class ExtCounter(Elaboratable):
  def __init__(self):
    self.o = Signal()

  def elaborate(self, platform):
    m = Module()

    # Declare a new clock domain
    m.domains.ext = ClockDomain('ext')
    # Get 'ext_clock' resource from the platform
    ext_clock = platform.request('ext_clock')
    # Bind the ext_clock to the clock signal of our new clock domain
    m.d.comb += ClockSignal('ext').eq(ext_clock)

    # Increment counter based on external clock signal
    counter = Signal(22)
    m.d.ext += counter.eq(counter + 1)

    # Bind the highest bit of our counter to the input of FFSynchronizer
    # and bind the output of FFSynchronizer to self.o
    m.submodules.ffsync = FFSynchronizer(counter[-1], self.o)

    return m

if __name__ == '__main__':
  ext_counter = ExtCounter()
  main(ext_counter)
