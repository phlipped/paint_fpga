from nmigen import *

from tinyfpga_paint_control_platform import PaintControlPlatform

from spi import SpiCore, SpiRegIf

class SpiCoreOnPlatform(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        spi_core = SpiCore(8)
        platform_spi = platform.request("spi")
        m.d.comb += [
            spi_core.spi_clk.eq(platform_spi.clk),
            spi_core.ss.eq(platform_spi.ss),
            spi_core.mosi.eq(platform_spi.mosi),
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
