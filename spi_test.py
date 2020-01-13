from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from pudb import set_trace

from spi import *

class SpiCoreTest(FHDLTestCase):
    def setUp(self):
        self.width = 9
        self.dut = SpiCore(self.width)

    def testDataIn(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1e-6, domain='spi_rising')
        def process():
            bit_pattern = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                           1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                           0, 1, 0, 1, 1, 0, 0, 1, 1, 0,
                           0, 1, 0, 1]
            yield self.dut.ss.eq(0)
            yield Settle()
            for i, b in enumerate(bit_pattern[self.width-1:]):
                yield self.dut.mosi.eq(b)
                yield Settle()
                yield
                yield Settle()
                bits = bit_list_to_number(bit_pattern[i:i+self.width])
                assert (yield self.dut.i_reg == bits)
        sim.add_sync_process(process, domain='spi_rising')
        with sim.write_vcd(
            "test_output/spi_core_test_data_in.vcd",
            "test_output/spi_core_test_data_in.gtkw"):
            sim.run()

    def testDataOut(self):
        bit_pattern = [1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 1, 0, 0, 1, 1, 0,]
        words_to_test = len(bit_pattern) // self.width
        sim = Simulator(self.dut)
        sim.add_clock(1e-6, domain='spi_rising')
        miso_out = []
        def record_miso_process():
            yield Passive()
            while True:
                yield
                miso_out.append((yield self.dut.miso))
        sim.add_sync_process(record_miso_process, domain='spi_falling')
        def process():
            yield Delay(1e-8)
            yield self.dut.ss.eq(0)
            yield Delay(1e-8)
            for i in range(words_to_test):
                # wait for o_count to be non-zero - this means we're ready to load o_reg
                while ((yield self.dut.out_count) != 0):
                    yield Delay(1e-08)

                bits = bit_pattern[i*self.width:i*self.width + self.width]
                val = bit_list_to_number(bits)
                yield self.dut.o_reg.eq(val)

                # wait for o_count to be 0 - this means our value has been loaded
                while ((yield self.dut.out_count) == 0):
                    yield Delay(1e-08)

            # wait for o_count to be non-zero - that means it's started being pumped out
            while ((yield self.dut.out_count) != 0):
                yield Delay(1e-08)

            # wait for zero - that means it's finished being pumped out
            while ((yield self.dut.out_count) == 0):
                yield Delay(1e-08)

            # wait for o_count to be non-zero - that means it's started being pumped out
            while ((yield self.dut.out_count) != 0):
                yield Delay(1e-08)

            # wait for zero - that means it's finished being pumped out
            while ((yield self.dut.out_count) == 0):
                yield Delay(1e-08)
        sim.add_process(process)
        with sim.write_vcd(
            "test_output/spi_core_test_data_out.vcd",
            "test_output/spi_core_test_data_out.gtkw",
            ):
            sim.run()
        expected_miso_out = ([0] * self.width) + bit_pattern[:words_to_test * self.width]
        assert expected_miso_out == miso_out

class SpiRegIfTest(FHDLTestCase):
    def setUp(self):
        width = 8
        read_regs = Array([Signal(width) for x in range(5)])
        write_regs = Array([Signal(width) for x in range(5)])
        self.dut = SpiRegIf(read_regs, write_regs)

    def pump_spi_clk(self):
        yield self.dut.spi_clk.eq(1)
        yield Delay(1e-8)
        yield self.dut.spi_clk.eq(0)
        yield Delay(1e-8)

    def send_mosi_bits(self, bits):
        for b in bits:
            yield self.dut.mosi.eq(b)
            yield from self.pump_spi_clk()

    def send_read_addr(self, addr):
        addr_as_list_of_7_bits = number_to_bit_list(addr, 7)
        yield from self.send_mosi_bits([0] + addr_as_list_of_7_bits)

    def send_write_addr_val(self, addr, val):
        addr_as_list_of_7_bits = number_to_bit_list(addr, 7)
        yield from self.send_mosi_bits([1] + addr_as_list_of_7_bits)
        val_as_list_of_8_bits = number_to_bit_list(val, 8)
        yield from self.send_mosi_bits(val_as_list_of_8_bits)

    def test0(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1e-9, domain='sync')
        def process():
            yield
            yield self.dut.ss.eq(0)
            yield
            yield from self.send_write_addr_val(3, 59)
            yield from self.send_write_addr_val(1, 127)
            yield from self.send_write_addr_val(5, 88)
            yield from self.send_read_addr(3)
            yield from self.send_mosi_bits([0] * 8)
            yield

            yield from self.pump_spi_clk()
        sim.add_sync_process(process)
        with sim.write_vcd(
            "test_output/spi_reg_if_test0.vcd",
            "test_output/spi_reg_if_test0.gtkw"):
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
