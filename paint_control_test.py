from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from paint_control import *

class PaintControlTest(FHDLTestCase):
    def setUp(self):
        self.dut = PaintControl()

    def test0(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1/16000000)
        def process():
            yield
            yield
        sim.add_sync_process(process)
        with sim.write_vcd(
            "test_output/paint_control_test_init.vcd",
            "test_output/paint_control_test_init.gtkw"):
            sim.run()
