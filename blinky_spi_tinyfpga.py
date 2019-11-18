from nmigen import *
from nmigen_boards import tinyfpga_bx
from nmigen.build import *

from blinky_spi import BlinkySpi

extensions = [
     Resource('blinky_spi', 0,
              Subsignal('spi_clk', Pins("A2", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS33")),
              Subsignal("ss", Pins("A1", dir="i")),
              Subsignal("mosi", Pins("B1", dir="i")),
              Attrs(IO_STANDARD="SB_LVCMOS33")),
     Resource('blinky_reset', 0, Pins("C2"),
              Attrs(IO_STANDARD="SB_LVCMOS33")),
     Resource('port', 0,
              Pins("C1 D2 D1 E2 E1 G2 H1 J1"),
              Attrs(IO_STANDARD="SB_LVCMOS33")),
     Resource('port', 1,
              Pins("H2 H9 D9 D8 C9 A9 B8 A8"),
              Attrs(IO_STANDARD="SB_LVCMOS33")),
]

class BlinkySpiTinyFPGA(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        # Disable USB by disabling by setting its pullup to 0
        usbpu = platform.request("usb").pullup
        m.d.comb += usbpu.eq(0)

        led = platform.request("user_led")
        blinky_spi_port = platform.request("blinky_spi")

        m.submodules.blinky_spi = blinky_spi = BlinkySpi()
        # m.d.comb += (led.eq(blinky_spi.blink_out),
        #              blinky_spi.spi.spi_clk.eq(blinky_spi_port.spi_clk),
        #              blinky_spi.spi.ss.eq(blinky_spi_port.ss),
        #              blinky_spi.spi.mosi.eq(blinky_spi_port.mosi))

        return m

        # Wire up some internals
        # port0 = plat.request("port", 0)
        # self.comb += port0.eq(self.blinky_spi.spi.input_buf)
        # port1 = plat.request("port", 1)
        # self.comb += port1[0].eq(self.blinky_spi.spi.data_in_ready)
        # self.comb += port1[1:3].eq(self.blinky_spi.spi.bit_count)
        # self.comb += port1[4:6].eq(self.blinky_spi.spi.spi_edge.buf)

if __name__ == "__main__":
    plat = tinyfpga_bx.TinyFPGABXPlatform()
    plat.add_resources(extensions)
    plat.build(BlinkySpiTinyFPGA(), do_program=True)
