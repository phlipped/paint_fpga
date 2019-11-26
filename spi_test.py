from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from spi import ShiftRegister

class ShiftRegisterTest(FHDLTestCase):
    def setUp(self):
        self.dut = ShiftRegister(10)

    def test_0(self):
        with Simulator(
            self.dut,
            vcd_file=open("shift_register.vcd", "w"),
            gtkw_file=open("shift_register.gtkw", "w"),
            traces=[self.dut.i, self.dut.reg, self.dut.o]) as sim:
            sim.add_clock(1e-6)
            def process():
                assert (yield self.dut.reg == 0)
                assert (yield self.dut.i == 0)
                assert (yield self.dut.o == 0)
                for i in [1, 1, 0, 0, 1, 1, 0, 1, 0, 1]:
                    yield self.dut.i.eq(i) # This only gets asserted at the next clock cycle
                    yield
                yield # need one more clock to update the circuit to the value
                assert (yield self.dut.reg == 0b1100110101)
                yield # one more clock will push the first bit out to the output
                assert (yield self.dut.o == 1)
                assert (yield self.dut.reg == 0b1001101011)
            sim.add_sync_process(process())
            sim.run()