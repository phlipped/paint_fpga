N = None
WRITE = 1
READ = 2

def RunTest(dut, pads, test_vals, sys_clk_per_iter=1):
  """RunTest is a simple testing framework.

  RunTest takes a device, some pads (presumably connected to the device),
  and an array of pad values.

  Each pad is a tuple of (Signal, DIR), where DIR is either READ or WRITE
  The DIR of a pad controls whether RunTest will try to set the value at each
  clock step (WRITE), or whether RunTest will try to verify the value (READ)

  The test_vals is a list of lists. The sub-lists must be exactly len(pads) long,
  and each value in the list sets the corresponding value of the pad at the same
  position in <pads>. The values can be 0, 1 or N.

  For READ pads, a value of N means "don't care" ie, the value will not be
  checked at that particular time.

  For WRITE pads, a value of N indicates that the value should not be
  asserted one way or the other, which typically means it will keep the same
  value as before.

  Assertion of WRITE pads occurs before the the clock is advanced, while
  verification of READ values happens after the clock is advanced.

  sys_clk_per_iter controls how many clock iterations should happen
  between each set of data values from in test_values.


  """
  writers = [i for i in range(len(pads)) if pads[i][1] == WRITE]
  readers = [i for i in range(len(pads)) if pads[i][1] == READ]

  for t in range(len(test_vals)):
    vals = test_vals[t]

    # Set ios
    for w in writers:
      val = vals[w]
      if val is not None:
        yield pads[w][0].eq(val)

    # Advance Clock
    for i in range(sys_clk_per_iter):
      yield

    # Read ios
    for r in readers:
      want_val = vals[r]
      if want_val is not None:
        got_val = yield pads[r][0]
        assert (want_val == got_val), "wrong Signal on pad %d  at clock %d. Want %d, got %d" % (r, t, want_val, got_val)
