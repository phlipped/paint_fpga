from nmigen import *

from tinyfpga_paint_control_platform import PaintControlPlatform

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
            spi_core.mosi.eq(spi_ss_sync[-1]),
            platform_spi.miso.eq(spi_core.miso),
        ]


        m.submodules += spi_core
        return m

class SpiRegIfOnPlatform(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        return m

if __name__ == "__main__":
    platform = PaintControlPlatform()
    platform.build(SpiCoreOnPlatform(platform), do_program=False)

    #platform = PaintControlPlatform()
    #platform.build(SpiRegIfOnPlatform(platform), do_program=False)
