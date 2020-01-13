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

    def send_read_addr(self, addr):
        addr_as_list_of_7_bits = number_to_bit_list(addr, 7)
        yield from self.send_mosi_bits([0] + addr_as_list_of_7_bits)

    def send_write_addr_val(self, addr, val):
        addr_as_list_of_7_bits = number_to_bit_list(addr, 7)
        mosi_bits = [1] + addr_as_list_of_7_bits
        yield from self.send_mosi_bits(mosi_bits)
        val_as_list_of_8_bits = number_to_bit_list(val, 8)
        yield from self.send_mosi_bits(val_as_list_of_8_bits)

    def test0(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1/16000000)
        def process():
            yield
            yield
        sim.add_sync_process(process)
        with sim.write_vcd(
            "test_output/paint_control_test0.vcd",
            "test_output/paint_control_test0.gtkw"):
            sim.run()

    def test1(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1/16000000)
        def process():
            yield
            yield self.dut.ss.eq(0)
            yield
            yield from self.send_write_addr_val(1, 0x10)
            yield from self.send_write_addr_val(2, 0x00)
            yield from self.send_write_addr_val(3, 0x00)
            yield from self.send_write_addr_val(4, 0x00)
            yield from self.send_write_addr_val(0, 0x02)
            yield Delay(7e-5)
            yield self.dut.fsm.motor_enables[0].limit_top.eq(1)
            yield Delay(1e-4)
        sim.add_sync_process(process)
        with sim.write_vcd(
            "test_output/paint_control_test1.vcd",
            "test_output/paint_control_test1.gtkw"):
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
