from migen import *

class EdgeDetect(Module):
  def __init__(self, sig, buf_depth=3, rising=True, falling=True):
    self.rising = Signal() if rising else None
    self.falling = Signal() if falling else None

    ###

    buf = Signal(buf_depth)
    self.sync += buf.eq(Cat(sig, buf[0:-1]))
    if rising:
      self.sync += self.rising.eq(buf[-2:] == 0b01)
    if falling:
      self.sync += self.falling.eq(buf[-2:] == 0b10)
