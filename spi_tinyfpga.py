from nmigen import *
from nmigen_boards import tinyfpga_bx
from nmigen.build import *

from spi import Spi

extensions = [
     Resource('spi_port', 0,
              Subsignal('spi_clk', Pins("A2", dir="i"), Clock(16e6), Attrs(IO_STANDARD="SB_LVCMOS33")),
              Subsignal("ss", Pins("A1", dir="i")),
              Subsignal("mosi", Pins("B1", dir="i")),
              Attrs(IO_STANDARD="SB_LVCMOS33")),
]

class SpiTiny(Elaboratable):
    def __init__(self, width=8):
        self.spi_clk_src = Signal()
        self.ss = Signal()  # FIXME make reset inverted?
        self.mosi = mosi = Signal()
        self.miso = miso = Signal()
        self.in_reg = Signal(width)
        self.in_reg_ready = Signal()

    def elaborate(self, platform):
        m = Module()

        m.domains.sync = ClockDomain()
        m.domains.spi = ClockDomain()

        # Drive the spi_domain clock using the aligned spi clock
        m.d.comb += ClockSignal("spi").eq(self.spi_clk_src)

        bit_count = Signal(range(0, len(self.in_reg)))

        with m.If(~self.ss):
            # Increment counter
            m.d.spi += bit_count.eq(bit_count + 1)

            # When counter is at max
            with m.If(bit_count == (2**(len(bit_count)) - 1)):
                m.d.spi += (self.in_reg_ready.eq(1))
            with m.Else():
                m.d.spi += self.in_reg_ready.eq(0)

            # Shift data into in_reg
            m.d.spi += self.in_reg.eq(Cat(self.mosi, self.in_reg[:-1]))
        with m.Else():
            # ss is high, so reset
            # FIXME try to re-use built-in reset to achieve this?
            m.d.spi += (self.in_reg.eq(0),
                        self.in_reg_ready.eq(0),
                        bit_count.eq(0))
        return m

class SpiTinyFPGA(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        # Disable USB by disabling by setting its pullup to 0
        usbpu = platform.request("usb").pullup
        m.d.comb += usbpu.eq(0)

        m.submodules += SpiTiny()

        return m

if __name__ == "__main__":
    plat = tinyfpga_bx.TinyFPGABXPlatform()
    plat.add_resources(extensions)
    # import pudb; pudb.set_trace()
    plat.build(SpiTinyFPGA(), do_program=True)
