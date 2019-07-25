from migen import *
from shift_register import ShiftRegister

class Spi(Module):
  '''Basic Spi shift register thing.

  Currently only does reads - you can't write data to it
  Doesn't do anything clever with 'addresses' or 'commands'.
  It just reads words the length of the data register and tells you when it's received a full word
  '''
  def __init__(self, word_size=8):
    self.miso = miso = Signal()
    self.mosi = mosi = Signal()
    self.ss = ss = Signal()
    self.spi_clk = Signal()
    self.submodules.reg = ShiftRegister(word_size)

    ###

    bit_count = Signal(max=word_size) # Count number of bits received.

    # On the spi clk ...
    #  - increment bit_count
    #    - if we hit the bit_count limit, set data_in_ready
    #  - shift mosi into data_in register
    self.sync += If(~ss,
                        bit_count.eq(bit_count + 1),
                        data_in.eq(Cat(mosi, data_in[:-1])),
                        If(bit_count == word_size-1,
                           data_in_ready.eq(1)
                        ).Else(
                           data_in_ready.eq(0)
                        )
                     ).Else( # ss is high, so keep resetting everything
                             # Could also only do this on ss rising or falling
                             # edge, but may as well just do it all the time
                             # while ss is high, right?
                        data_in.eq(0),
                        bit_count.eq(0),
                        data_in_ready.eq(0),
                    )
