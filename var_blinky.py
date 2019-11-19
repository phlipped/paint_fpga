from nmigen import *
from nmigen_boards.tinyfpga_bx import *
from nmigen.build import Resource, Pins

class VarBlinky(Elaboratable):
    '''VarBlinky blinks the led, with speed determined by speed input'''
    def elaborate(self, platform):
        led = platform.request("led", 0)
        speed = platform.request("speed", 0)

        m = Module()

        timer = Signal(24)
        m.d.sync += timer.eq(timer + 1)

        # <led> is bound to the last or second last bit of timer, depending on
        # <speed>
        with m.If(speed == 1):
            m.d.comb += led.eq(timer[-2])
        with m.Else():
            m.d.comb += led.eq(timer[-1])

        return m

class TinyFPGAForBlinky(TinyFPGABXPlatform):
    resources = TinyFPGABXPlatform.resources + [
        Resource("speed", 0, Pins("4", conn=("gpio", 0), dir="i")),
    ]


if __name__ == "__main__":
    platform = TinyFPGAForBlinky()
    platform.build(VarBlinky(platform), do_program=True)
