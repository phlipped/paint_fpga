from nmigen import *
from nmigen_boards import tinyfpga_bx
from nmigen.build import *
import pudb

extensions = [
    Resource("ext", 0, Pins("A2", dir="i"),
                 Clock(16e6), Attrs(IO_STANDARD="SB_LVCMOS33")),
    Resource('cdc_exp_output', 0, Pins("C2"),
                 Attrs(IO_STANDARD="SB_LVCMOS33")),
     # Resource('blinky_spi', 0,
     #          Subsignal("ss", Pins("A1", dir="i")),
     #          Subsignal("mosi", Pins("B1", dir="i")),
     #          Attrs(IO_STANDARD="SB_LVCMOS33")),
     # Resource('blinky_reset', 0, Pins("C2"),
     #          Attrs(IO_STANDARD="SB_LVCMOS33")),
     # Resource('port', 0,
     #          Pins("C1 D2 D1 E2 E1 G2 H1 J1"),
     #          Attrs(IO_STANDARD="SB_LVCMOS33")),
     # Resource('port', 1,
     #          Pins("H2 H9 D9 D8 C9 A9 B8 A8"),
     #          Attrs(IO_STANDARD="SB_LVCMOS33")),
]

class CdcExp(Elaboratable):
    '''Testing external CD or something.'''
    def elaborate(self, platform):
        m = Module()

        output = Signal()
        m.domains += ClockDomain("ext")
        m.d.comb += ClockSignal("ext").eq(platform.request("ext"))
        m.d.ext += output.eq(~output)
        m.d.comb += platform.request("cdc_exp_output").o.eq(output)

        return m

class Blinky(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        led = platform.request("user_led").o

        ctr = Signal(max=int(8e6//2), reset=int(16e6//2) - 1)
        with m.If(ctr == 0):
            m.d.sync += ctr.eq(ctr.reset)
            m.d.sync += led.eq(~led)
        with m.Else():
            m.d.sync += ctr.eq(ctr - 1)

        return m

if __name__ == '__main__':
    # pudb.set_trace()
    plat = tinyfpga_bx.TinyFPGABXPlatform()
    plat.add_resources(extensions)
    # cdc_exp = CdcExp()
    plat.build(CdcExp(), do_program=False)
    # cdc_exp = CdcExp()
    # main(cdc_exp, ports=[cdc_exp.ext_clk, cdc_exp.output])
