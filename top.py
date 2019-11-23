from nmigen import *
from nmigen.cli import main
from nmigen_boards import tinyfpga_bx
from nmigen.build import Resource, Pins

from ext_counter import ExtCounter

extensions = [
    Resource('ext_clock', 0, Pins("C2", dir="i")),
    Resource('main_clock_out', 0, Pins("C1 D2 D1 E2", dir="o"))
]

class Top(Elaboratable):
  def elaborate(self, platform):
    m = Module()
    ext = ExtCounter()
    m.submodules.ext = ext

    led = platform.request('led')
    main_clock_out = platform.request('main_clock_out')
    counter = Signal(22)
    flops_from_ext = Signal(3)

    m.d.sync += [counter.eq(counter + 1),
                 flops_from_ext[0].eq(ext.count),
                 flops_from_ext[1:].eq(flops_from_ext[:-1]),
                 led.eq(flops_from_ext[-1]),]

    # Bind 5 bits of main_clock_out to the bottom 5 bits of self.counter
    m.d.comb += [main_clock_out.eq(counter[:4])]

    return m

if __name__ == '__main__':
  plat = tinyfpga_bx.TinyFPGABXPlatform()
  plat.add_resources(extensions)
  plat.build(Top(), do_program=False)
