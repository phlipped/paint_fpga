from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from motor_enable import *

class MoterEnableTest(FHDLTestCase):
    def setUp(self):
        self.dut = MotorEnable()

    def test_0(self):
        with open("motor_enable.vcd", "w") as vcd_file, open("motor_enable.gtkw", "w") as gtkw_file, Simulator(
            self.dut,
            vcd_file=vcd_file,
            gtkw_file=gtkw_file) as sim:
            sim.add_clock(1e-6)
            def process():
                for dir, limit in [(1, self.dut.limit_bottom), (0, self.dut.limit_top)]:
                    yield self.dut.direction.eq(dir)     # down
                    yield limit.eq(0)
                    yield self.dut.enable_i.eq(1)
                    yield
                    assert (yield self.dut.enable_o == 1)
                    yield self.dut.enable_i.eq(0)
                    yield
                    assert (yield self.dut.enable_o == 0)
                    yield self.dut.enable_i.eq(1)
                    yield
                    assert (yield self.dut.enable_o == 1)
                    yield self.dut.enable_i.eq(0)
                    yield
                    assert (yield self.dut.enable_o == 0)
                    yield limit.eq(1)
                    yield self.dut.enable_i.eq(1)
                    yield
                    assert (yield self.dut.enable_o == 0)
                    yield self.dut.enable_i.eq(0)
                    yield
                    assert (yield self.dut.enable_o == 0)
                    yield self.dut.enable_i.eq(1)
                    yield
                    assert (yield self.dut.enable_o == 0)
                    yield self.dut.enable_i.eq(0)
                    yield
                    assert (yield self.dut.enable_o == 0)
            sim.add_sync_process(process())
            sim.run()
