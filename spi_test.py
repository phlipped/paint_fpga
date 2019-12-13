from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from pudb import set_trace

from spi import *

class SpiCoreTest(FHDLTestCase):
    def setUp(self):
        self.width = 9
        self.dut = SpiCore(self.width)

    def test_dataIn(self):
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
            "spi_core_test_data_in.vcd",
            "spi_core_test_data_in.gtkw"):
            sim.run()

    def test_dataOut(self):
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
            "spi_core_test_data_out.vcd",
            "spi_core_test_data_out.gtkw",
            ):
            sim.run()
        expected_miso_out = ([0] * self.width) + bit_pattern[:words_to_test * self.width]
        assert expected_miso_out == miso_out

def bit_list_to_number(bits):
    bit_string = ''.join([str(b) for b in bits])
    return int(bit_string, 2)

def shift_left(val, size):
    val = val << 1
    ones = pow(2, size) - 1
    val = val & ones
    return val
