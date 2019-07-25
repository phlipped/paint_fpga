from migen import *

class Spi(Module):
  '''Basic Spi shift register thing.

  Currently only does reads - you can't write data to it
  Doesn't do anything clever with 'addresses' or 'commands'.
  It just reads words the length of the data register and tells you when it's received a full word
  '''
  def __init__(self, word_size=8):
    self.spi_clk = spi_clk = Signal() # input
    self.ss = ss = Signal() # input
    self.miso = miso = Signal()
    self.mosi = mosi = Signal()
    self.data_in_ready = data_in_ready = Signal()
    self.data_in = data_in = Signal(word_size)

    ###

    bit_count = Signal(max=word_size) # Count number of bits received.
    self.submodules.spi_edge = EdgeDetect(spi_clk, falling=False)

    # If ss is low and we receive an spi_rising edge
    #  - increment bit_count
    #    - if we hit the bit_count limit, set data_in_ready
    #  - shift mosi into data_in register
    self.sync += If(~ss,
                    If(self.spi_edge.rising,
                       If(bit_count == word_size - 1,
                          bit_count.eq(0)
                       ).Else(
                         bit_count.eq(bit_count + 1)
                       ),
                       data_in.eq(Cat(mosi, data_in[:-1])),
                       If(bit_count == word_size-1,
                          data_in_ready.eq(1)
                       ).Else(
                          data_in_ready.eq(0)
                       )
                    )
                    ).Else (
                        self.data_in_ready.eq(0),
                        self.data_in.eq(0),
                        bit_count.eq(0),
                    )

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
