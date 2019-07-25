from migen import *
from shift_reg import ShiftReg
from testing import RunTest, WRITE, READ, N

test1 = [
    (1, N, 0x00), (0, N, 0x01), (1, N, 0x02), (0, N, 0x05),
    (1, N, 0x0A), (1, N, 0x15), (0, N, 0x2B), (0, N, 0x56),
    (0, 0, 0xAC), (0, 1, 0x58), (0, 0, 0xB0), (0, 1, 0x60),
    (0, 0, 0xC0), (0, 1, 0x80), (0, 1, 0x00), (0, 0, 0x00),
    (0, 0, 0x00),
]

if __name__ == '__main__':
  for test_data in [test1]:
    dut = ShiftReg()
    pads = ((dut.input, WRITE), (dut.output, READ), (dut.reg, READ)),
    run_simulation(dut, RunTest(dut, pads, test_data), vcd_name="shift_reg_sim.vcd")
