from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from paint_control import *

class PaintControlTest(FHDLTestCase):
    def setUp(self):
        self.dut = PaintControl()

    def pump_spi_clk(self):
        yield self.dut.spi_clk.eq(1)
        yield Delay(1e-6)
        yield self.dut.spi_clk.eq(0)
        yield Delay(1e-6)

    def send_mosi_bits(self, bits):
        for b in bits:
            yield self.dut.mosi.eq(b)
            yield from self.pump_spi_clk()

    def spi_read(self, addr):
        addr_as_list_of_7_bits = number_to_bit_list(addr, 7)
        yield from self.send_mosi_bits([0] + addr_as_list_of_7_bits)

    def spi_write(self, addr, val):
        addr_as_list_of_7_bits = number_to_bit_list(addr, 7)
        mosi_bits = [1] + addr_as_list_of_7_bits
        yield from self.send_mosi_bits(mosi_bits)
        val_as_list_of_8_bits = number_to_bit_list(val, 8)
        yield from self.send_mosi_bits(val_as_list_of_8_bits)

    def test_colour0_15_steps_down(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1/16000000)
        def process():
            yield
            yield
            yield
            yield self.dut.ss.eq(0)
            yield
            yield from self.spi_write(2, 320) # PWM TOP Low Byte = 20 us
            yield from self.spi_write(4, 16) # PWM MATCH Low Byte - 16 = 1us
            yield from self.spi_write(6, 15)   # Colour 0 Lowest Byte
            yield from self.spi_write(10, 10)   # Colour 1 lowest byte
            yield from self.spi_write(1, 0b00000010) # DISPENSING MODE
            yield Delay(2e-4)
            yield from self.spi_write(1, 0x01) # Reset
            yield from self.spi_write(1, 0x00) # Un-reset
        sim.add_sync_process(process)
        with sim.write_vcd(
            "test_output/paint_control_test_colour0_15_steps_down.vcd",
            "test_output/paint_control_test_colour0_15_steps_down.gtkw"):
            sim.run()


def bit_list_to_number(bits):
    bit_string = ''.join([str(b) for b in bits])
    return int(bit_string, 2)

def number_to_bit_list(n, pad):
    return list(reversed([(n >> x) & 1 for x in range(pad)]))

def shift_left(val, size):
    val = val << 1
    ones = pow(2, size) - 1
    val = val & ones
    return val
