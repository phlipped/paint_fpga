from nmigen import *
from nmigen.test.utils import *
from nmigen.back.pysim import *

from spi import *

class ShiftRegisterTest(FHDLTestCase):
    def setUp(self):
        self.dut = ShiftRegister(10)

    def test_0(self):
        with open("shift_register.vcd", "w") as vcd_file, open("shift_register.gtkw", "w") as gtkw_file, Simulator(
                  self.dut,
                  vcd_file=vcd_file,
                  gtkw_file=gtkw_file,
                  traces=[self.dut.i, self.dut.reg, self.dut.o]) as sim:
            sim.add_clock(1e-6)
            def process():
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

class ShiftRegisterWithDataReadyTest(FHDLTestCase):
    def setUp(self):
        self.dut = ShiftRegisterWithDataReady(10)

    def test_0(self):
        with Simulator(
            self.dut,
            vcd_file=open("shift_register_with_data_ready_test_0.vcd", "w"),
            gtkw_file=open("shift_register_with_data_ready_test_0.gtkw", "w"),
            traces=[self.dut.i, self.dut.reg, self.dut.o, self.dut.data_ready, self.dut.count]) as sim:
            sim.add_clock(1e-6)
            def process():
                bit_pattern = [1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                               0, 1, 0, 1, 1, 0, 0, 1, 1, 0,
                               0, 1, 0, 1]
                for i, b in enumerate(bit_pattern):
                    yield self.dut.i.eq(b) # This only gets asserted at the next clock cycle
                    yield
                    if (i % 10) == 0 and i != 0:
                        assert (yield self.dut.data_ready == 1)

            sim.add_sync_process(process())
            sim.run()

class EdgeDetectTest(FHDLTestCase):
  def setUp(self):
    self.dut = EdgeDetect()

  def test_rising(self):
    with Simulator(self.dut) as sim:
      sim.add_clock(1e-6)
      def process():
        yield self.dut.i.eq(1)
        yield # self.dut.i is now 1
        yield # reg should now be [1000]
        yield # reg should now be [1100]
        yield # reg should now be [1110]
        assert not (yield self.dut.rising)
        yield
        assert (yield self.dut.rising)
        yield
        assert not (yield self.dut.rising)
      sim.add_sync_process(process())
      sim.run()

  def test_falling(self):
    with Simulator(self.dut) as sim:
      sim.add_clock(1e-6)
      def process():
        yield self.dut.i.eq(1)
        yield # self.dut.i is now 1
        yield self.dut.i.eq(0)
        yield # reg should now be [1000], self.dut.i is now 0
        yield # reg should now be [0100]
        yield # reg should now be [0010]
        yield # reg should now be [0001]
        assert not (yield self.dut.falling)
        yield
        assert (yield self.dut.falling)
        yield
        assert not (yield self.dut.falling)
      sim.add_sync_process(process())
      sim.run()

class SpiCoreTest(FHDLTestCase):
    def setUp(self):
        self.width = 10
        self.dut = SpiCore(self.width)

    def SpiClock(self):
        yield from self.SpiRise()
        yield from self.SpiFall()

    def SpiRise(self):
        yield self.dut.spi_clk.eq(1)
        for i in range(6):
            yield

    def SpiFall(self):
        yield self.dut.spi_clk.eq(0)
        for i in range(6):
            yield

    def test_dataIn(self):
        with open("spi_core_test_data_in.vcd", "w") as vcd_file, open("spi_core_test_data_in.gtkw", "w") as gtkw_file, Simulator(
            self.dut,
            vcd_file=vcd_file,
            gtkw_file=gtkw_file,
            traces=[self.dut.i_reg, self.dut.mosi, self.dut.spi_clk]) as sim:
            sim.add_clock(1e-6)
            def process():
                bit_pattern = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                               1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                               0, 1, 0, 1, 1, 0, 0, 1, 1, 0,
                               0, 1, 0, 1]
                yield self.dut.ss.eq(0)
                yield
                for i, b in enumerate(bit_pattern[self.width-1:]):
                    yield self.dut.mosi.eq(b)
                    yield from self.SpiClock()
                    bits = bit_list_to_number(bit_pattern[i:i+self.width])
                    assert (yield self.dut.i_reg == bits)
            sim.add_sync_process(process())
            sim.run()

    def test_dataOut(self):
        print()
        with open("spi_core_test_data_out.vcd", "w") as vcd_file, open("spi_core_test_data_out.gtkw", "w") as gtkw_file, Simulator(
            self.dut,
            vcd_file=vcd_file,
            gtkw_file=gtkw_file,
            traces=[self.dut.o_reg, self.dut._o_reg, self.dut.miso, self.dut.spi_clk]) as sim:
            sim.add_clock(1e-6)
            def process():
                bit_pattern = [1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                               0, 1, 0, 1, 1, 0, 0, 1, 1, 0,]
                yield self.dut.ss.eq(0)
                yield
                for i in range(len(bit_pattern) // self.width):
                    bits = bit_pattern[i*self.width:i*self.width + self.width]
                    print("bitset #{}: {}".format(i, bits))
                    val = bit_list_to_number(bits)
                    yield self.dut.o_reg.eq(val)
                    yield # load o_reg
                    yield # load o_reg into _o_reg
                    assert ((yield self.dut._o_reg) == (yield self.dut.o_reg))
                    for j in range(self.width):
                        print("bit: #{} == {}".format(j, bits[j]))
                        expected_miso = yield self.dut._o_reg[-1]
                        print("expected_miso: {}".format(expected_miso))
                        yield from self.SpiClock()
                        miso = yield self.dut.miso
                        print("miso: {}".format(miso))
                        assert (miso == expected_miso)

            sim.add_sync_process(process())
            sim.run()

def bit_list_to_number(bits):
    bit_string = ''.join([str(b) for b in bits])
    return int(bit_string, 2)

def shift_left(val, size):
    val = val << 1
    ones = pow(2, size) - 1
    val = val & ones
    return val
