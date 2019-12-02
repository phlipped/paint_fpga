from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from motor_enable import *

class ShiftRegisterTest(FHDLTestCase):
    def setUp(self):
        self.dut = MotorEnable()

    def test_0(self):
        with open("motor_enable.vcd", "w") as vcd_file, open("motor_enable.gtkw", "w") as gtkw_file, Simulator(
            self.dut,
            vcd_file=vcd_file,
            gtkw_file=gtkw_file) as sim:
            sim.add_clock(1e-6)
            def process():
                yield self.dut.direction.eq(1)
                yield self.dut.limit_bottom.eq(0)
                yield self.dut.enable_i.eq(1)
                yield
                yield self.dut.enable_i.eq(0)
                yield
                yield self.dut.enable_i.eq(1)
                yield
                yield self.dut.enable_i.eq(0)
                yield
                yield self.dut.limit_bottom.eq(1)
                yield self.dut.enable_i.eq(1)
                yield
                yield self.dut.enable_i.eq(0)
                yield
                yield self.dut.enable_i.eq(1)
                yield
                yield self.dut.enable_i.eq(0)
                yield
            sim.add_sync_process(process())
            sim.run()
