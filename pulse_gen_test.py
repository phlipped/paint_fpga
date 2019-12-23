from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from pulse_gen import *

class PulseGenTest(FHDLTestCase):
    def setUp(self):
        self.dut = PulseGen()

    def test_8_10(self):
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1e-9)
        def process():
            yield self.dut.top.eq(10)
            yield self.dut.match.eq(8)
            yield
            yield
            yield self.dut.active.eq(1)
            for i in range(22):
                yield
        sim.add_sync_process(process)
        with sim.write_vcd(
            "pulse_gen_test_8_10.vcd",
            "pulse_gen_test_8_10.gtkw"):
            sim.run()
