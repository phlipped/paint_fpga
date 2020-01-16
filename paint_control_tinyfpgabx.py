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
        m.d.comb += [
            paint_control.spi_clk.eq(platform_spi.clk),
            paint_control.ss.eq(platform_spi.ss),
            paint_control.mosi.eq(platform_spi.mosi),
            platform_spi.miso.eq(paint_control.miso),

            platform.request("direction").eq(paint_control.direction),
            platform.request("steps").eq(paint_control.steps),
        ]

        for i in range(5):
            motor_signals = platform.request("motor_signals", i)
            m.d.comb += [
                motor_signals.enable_o.eq(paint_control.motor_signals[i].enable_o),
                paint_control.motor_signals[i].limit_top.eq(motor_signals.limit_top),
                paint_control.motor_signals[i].limit_bottom.eq(motor_signals.limit_bottom),
            ]

        m.submodules += paint_control

        return m

if __name__ == "__main__":
    platform = PaintControlPlatform()
    platform.build(PaintControlBoard(), do_program=True)
