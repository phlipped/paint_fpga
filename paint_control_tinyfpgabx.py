from nmigen import *
from nmigen_boards.tinyfpga_bx import *
from nmigen.build import Resource, Pins

from paint_control import PaintControl
from spi import SpiRegIf
from paint_control_fsm import *

from tinyfpga_paint_control_platform import PaintControlPlatform

class PaintControlBoard(Elaboratable):
    '''An instance of PaintControl where the Signals are requested from the platform'''
    def elaborate(self, platform):
        m = Module()

        # Create paint control sub module, wire it up
        paint_control = PaintControl()

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
            paint_control.spi_clk.eq(spi_clk_sync[-1]),
            paint_control.ss.eq(spi_ss_sync[-1]),
            paint_control.mosi.eq(spi_ss_sync[-1]),
            platform_spi.miso.eq(paint_control.miso),

            platform.request("direction").eq(paint_control.direction),
            platform.request("steps").eq(paint_control.steps),
        ]

        for i in range(5):
            motor_signals = platform.request("motor_signals", i)

            limit_top_sync = Signal(3)
            limit_bottom_sync = Signal(3)

            m.d.sync += [
                limit_top_sync.eq(Cat(motor_signals.limit_top, limit_top_sync[:-1])),
                limit_bottom_sync.eq(Cat(motor_signals.limit_bottom, limit_bottom_sync[:-1])),
            ]

            m.d.comb += [
                motor_signals.enable_o.eq(paint_control.motor_signals[i].enable_o),
                paint_control.motor_signals[i].limit_top.eq(limit_top_sync),
                paint_control.motor_signals[i].limit_bottom.eq(limit_bottom_sync),
            ]

        m.submodules += paint_control

        return m

if __name__ == "__main__":
    platform = PaintControlPlatform()
    platform.build(PaintControlBoard(), do_program=True)
