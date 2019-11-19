from nmigen import *
from nmigen_boards.tinyfpga_bx import *

class VarBlinky(Elaboratable):
    '''VarBlinky blinks the led, with speed determined by speed input'''
    def elaborate(self, platform):
        led = platform.request("led", 0)
        # speed = platform.request("gpio", 4)
        speed = Signal()

        m = Module()

        timer = Signal(24)
        m.d.sync += timer.eq(timer + 1)

        # led equals the last or second last bit of timer, depending on speed
        #with m.If(speed == 1):
        #    m.d.comb += led.eq(timer[-2])
        #with m.Else():
        #    m.d.comb += led.eq(timer[-1])

        m.d.comb += led.eq(timer[-1])

        return m

if __name__ == "__main__":
    platform = TinyFPGABXPlatform()
    platform.build(VarBlinky(platform), do_program=True)
