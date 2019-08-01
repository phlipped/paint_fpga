from migen import *

class EdgeDetect(Module):
  '''EdgeDetect Module.

  Generates a pulse when a rising and/or falling edge is detected on some
  input signal.

  Edge detection is implemented by marshalling the input signal <sig> through a
  shift register and comparing the two bits at the 'end' of the shift register
  to 0b01 (rising) or 0b10 (falling).

  The resulting rising/falling pulse will be delayed behind the actual edge,
  with larger buffer depths leading to larger delays. The average delay (in
  clock-widths) can be calculated with: (buf_depth - 1) + 0.5

  Signal Args:
    sig: Signal 1 x in
    rising: Signal 1 x out, or None/False to disable
    falling: Signal 1 x out, or None/False to disable

  Control Args:
    buf_depth: Depth of shift register buffer, default 3
  '''



  def __init__(self, sig, rising=None, falling=None, buf_depth=3):
    self.rising = rising
    self.falling = falling

    ###

    self.buf = buf = Signal(buf_depth)
    
    self.sync += buf.eq(Cat(sig, buf[0:-1]))
    if rising is not None:
      self.sync += self.rising.eq(buf[-2:] == 0b01)
    if falling is not None:
      self.sync += self.falling.eq(buf[-2:] == 0b10)
