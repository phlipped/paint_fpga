N = None
WRITE = 1
READ = 2

def RunTest(dut, pads, test_vals):
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
    yield

    # Read ios
    for r in readers:
      want_val = vals[r]
      if want_val is not None:
        got_val = yield pads[r][0]
        assert (want_val == got_val), "wrong Signal on pad %d  at clock %d. Want %d, got %d" % (r, t, want_val, got_val)
