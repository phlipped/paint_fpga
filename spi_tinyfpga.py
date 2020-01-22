from nmigen import *
from nmigen_boards.tinyfpga_bx import *
from nmigen.build import Resource, Pins, Subsignal

# rom tinyfpga_paint_control_platform import PaintControlPlatform

from spi import SpiCore, SpiRegIf

class SpiCoreOnPlatform(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        spi_core = SpiCore(8)
        platform_spi = platform.request("spi")

        # synchronise the SPI signals through some flip flops ...
        spi_clk_sync = Signal(3)
        spi_ss_sync = Signal(3)
        spi_mosi_sync = Signal(3)

        m.d.sync += [
            spi_clk_sync.eq(Cat(platform_spi.clk, spi_clk_sync[:-1])),
            spi_ss_sync.eq(Cat(platform_spi.ss, spi_ss_sync[:-1])),
            spi_mosi_sync.eq(Cat(platform_spi.mosi, spi_mosi_sync[:-1])),
        ]

        m.d.comb += [
            spi_core.spi_clk.eq(spi_clk_sync[-1]),
            spi_core.ss.eq(spi_ss_sync[-1]),
            spi_core.mosi.eq(spi_mosi_sync[-1]),
            platform_spi.miso.eq(spi_core.miso),
        ]

        m.submodules += spi_core

        m.d.sync += spi_core.o_reg.eq(spi_core.i_reg)

        p5 = platform.request("p5")
        p6 = platform.request("p6")
        p7 = platform.request("p7")
        p8 = platform.request("p8")
        p9 = platform.request("p9")
        p10 = platform.request("p10")
        p11 = platform.request("p11")
        p12 = platform.request("p12")

        debug_reg = Cat(spi_core._o_reg)

        m.d.comb += [
            p5.eq(debug_reg[0]),
            p6.eq(debug_reg[1]),
            p7.eq(debug_reg[2]),
            p8.eq(debug_reg[3]),
            p9.eq(debug_reg[4]),
            p10.eq(debug_reg[5]),
            p11.eq(debug_reg[6]),
            p12.eq(debug_reg[7]),
        ]

        return m

class SpiRegIfOnPlatform(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        width = 8
        read_regs = Array([Signal(width) for x in range(5)])
        write_regs = read_regs

        spi_reg_if = SpiRegIf(read_regs, write_regs)

        platform_spi = platform.request("spi")

        # synchronise the SPI signals through some flip flops ...
        spi_clk_sync = Signal(3)
        spi_ss_sync = Signal(3)
        spi_mosi_sync = Signal(3)

        m.d.sync += [
            spi_clk_sync.eq(Cat(platform_spi.clk, spi_clk_sync[:-1])),
            spi_ss_sync.eq(Cat(platform_spi.ss, spi_ss_sync[:-1])),
            spi_mosi_sync.eq(Cat(platform_spi.mosi, spi_mosi_sync[:-1])),
        ]

        m.d.comb += [
            spi_reg_if.spi_clk.eq(spi_clk_sync[-1]),
            spi_reg_if.ss.eq(spi_ss_sync[-1]),
            spi_reg_if.mosi.eq(spi_mosi_sync[-1]),
            platform_spi.miso.eq(spi_reg_if.miso),
        ]

        m.submodules += spi_reg_if

        p5 = platform.request("p5")
        p6 = platform.request("p6")
        p7 = platform.request("p7")
        p8 = platform.request("p8")
        p9 = platform.request("p9")
        p10 = platform.request("p10")
        p11 = platform.request("p11")
        p12 = platform.request("p12")

        debug_reg = Cat(spi_reg_if.addr)

        m.d.comb += [
            p5.eq(debug_reg[0]),
            p6.eq(debug_reg[1]),
            p7.eq(debug_reg[2]),
            p8.eq(debug_reg[3]),
            p9.eq(debug_reg[4]),
            p10.eq(debug_reg[5]),
            p11.eq(debug_reg[6]),
            p12.eq(debug_reg[7]),
        ]



        return m

pinDir = {
        # 1: "i", 2: "i", 3: "i", 4: "o",
        5: "o", 6: "o", 7: "o", 8: "o",
        9: "o", 10: "o", 11: "o", 12: "o",
        13: "o", 14: "i", 15: "i", 16: "i",
        17: "i", 18: "i", 19: "i", 20: "i",
        21: "i", 22: "i", 23: "i", 24: "i",
}

spi_resource = Resource(
    "spi",
    0,
    Subsignal("clk", Pins("1", conn=("gpio", 0), dir="i")),
    Subsignal("ss", Pins("2", conn=("gpio", 0), dir="i")),
    Subsignal("mosi", Pins("3", conn=("gpio", 0), dir="i")),
    Subsignal("miso", Pins("4", conn=("gpio", 0), dir="o")),
)

class PinsPlatform(TinyFPGABXPlatform):
    resources = (
        TinyFPGABXPlatform.resources +
        [ spi_resource ] +
        [Resource("p{}".format(p), 0, Pins(str(p), conn=("gpio", 0), dir=pinDir[p]))
         for p in range(5, 25)
        ]
    )



if __name__ == "__main__":
    platform = PinsPlatform()
    platform.build(SpiRegIfOnPlatform(platform), do_program=True)

    #platform = PaintControlPlatform()
    #platform.build(SpiRegIfOnPlatform(platform), do_program=False)
