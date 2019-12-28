from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from paint_control import *

class PaintControlTest(FHDLTestCase):
    def setUp(self):
        self.dut = PaintControl()

    def testReadyToStart(self):
        """Test that the FSM moves from Ready to Start when reset is asserted."""
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1e-9)
        def process():
            yield
            yield
            yield self.dut.control[0].eq(1)
            yield
            yield
            yield
            yield
            yield self.dut.control[0].eq(0)
            yield
            yield
            yield
        sim.add_sync_process(process)
        with sim.write_vcd(
            "paint_control_test_init.vcd",
            "paint_control_test_init.gtkw"):
            sim.run()

    def testDispensing(self):
        """Blah"""
        sim = Simulator(fragment=self.dut)
        sim.add_clock(1e-9)
        def process():
            yield self.dut.control[0].eq(1)
            yield self.dut.control[0].eq(0)
            yield self.dut.colours_in[0].eq(4)
            yield self.dut.control[1:3].eq(0b01)
            for i in range(100):
                yield
        sim.add_sync_process(process)
        with sim.write_vcd(
            "paint_control_test_dispensing.vcd",
            "paint_control_test_dispensing.gtkw"):
            sim.run()
