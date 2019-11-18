from nmigen import *

from nmigen_boards.icebreaker import ICEBreakerPlatform

class SubMod(Elaboratable):
    def __init__(self):
        self.i = Signal()
        self.o = Signal()

    def elaborate(self, platform):
        m = Module()

        m.d.sync += self.o.eq(self.i)

        return m


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        sw = platform.request("user_btn")
        led = platform.request("user_led")

        m.submodules.submod = submod = SubMod()

        m.d.comb += [
            submod.i.eq(sw.i),
            led.o.eq(submod.o),
        ]

        return m

plan = ICEBreakerPlatform().build(Top(), do_build=False)
