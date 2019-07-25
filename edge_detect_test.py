from migen import *
from edge_detect import EdgeDetect
from testing import RunTest, WRITE, READ, N

test1 = {
    'buf_depth': 3,
    'test_data': [
        [0, N, N], [1, N, N], [1, N, N], [1, N, N],
        [1, 1, N], [0, 0, N], [0, 0, N], [0, 0, N],
        [0, 0, 1], [1, 0, 0], [1, 0, 0], [1, 0, 0],
        [1, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0],
        [1, 0, 1], [0, 1, 0], [1, 0, 1], [0, 1, 0],
        [1, 0, 1],
    ]
}

test2 = {
    'buf_depth': 4,
    'sig':        '011110000111101010101',
    'rising': 'xxxxx1000000010000101',
    'falling':'xxxxxxxxx100000001010',
}


if __name__ == '__main__':
  for test_set in [test1]:
    sig = Signal()
    dut = EdgeDetect(sig, test_set['buf_depth'])
    pads = ((sig, WRITE), (dut.rising, READ), (dut.falling, READ))
    run_simulation(dut, RunTest(dut, pads, test_set['test_data']), vcd_name="edge_detect_sim.vcd")
