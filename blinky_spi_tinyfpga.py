from migen import *
from migen.build.platforms import tinyfpga_bx
from migen.build.generic_platform import Pins, IOStandard, Subsignal
from blinky_spi import BlinkySpi

extensions = [
    ('blinky_spi', 0,
     Subsignal("clk", Pins("A2")),
     Subsignal("ss", Pins("A1")),
     Subsignal("mosi", Pins("B1")),
     IOStandard('LVCMOS33')),
    ('blinky_reset', 0, Pins("C2"),
     IOStandard('LVCMOS33')),
    ('port', 0,
     Pins("C1 D2 D1 E2 E1 G2 H1 J1"),
     IOStandard('LVCMOS33')),
    ('port', 1,
     Pins("H2 H9 D9 D8 C9 A9 B8 A8"),
     IOStandard('LVCMOS33')),
]

class BlinkySpiTinyFPGA(Module):
    def __init__(self, plat):
        # Get the USB port and wire the pull up to 0 to disable it
        usbpu = plat.request("usb").pullup
        self.comb += usbpu.eq(0)

        led = plat.request("user_led")
        blinky_spi = plat.request("blinky_spi")

        self.submodules.blinky_spi = BlinkySpi(
            blinky_spi.clk,
            blinky_spi.ss,
            blinky_spi.mosi,
            led)

        # Wire up some internals
        port0 = plat.request("port", 0)
        self.comb += port0.eq(self.blinky_spi.spi.input_buf)
        port1 = plat.request("port", 1)
        self.comb += port1[0].eq(self.blinky_spi.spi.data_in_ready)
        self.comb += port1[1:3].eq(self.blinky_spi.spi.bit_count)
        self.comb += port1[4:6].eq(self.blinky_spi.spi.spi_edge.buf)


plat = tinyfpga_bx.Platform()
plat.add_extension(extensions)
plat.build(BlinkySpiTinyFPGA(plat))
