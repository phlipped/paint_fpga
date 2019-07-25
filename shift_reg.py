from migen import *

class ShiftReg(Module):
  """ShiftReg runs on the sys clock"""

  def __init__(self, size=8, input=True, output=True):
    self.input = Signal() if input else None # input source: input
    self.output = Signal() if output else None # output: output
    self.reg = Signal(size)

    ###

    if input:
      self.sync += self.reg.eq(Cat(self.input, self.reg[:-1])),
    if output:
      self.sync += self.output.eq(self.reg[-1]),

class ShiftRegExternalClk(Module):
  def __init__
