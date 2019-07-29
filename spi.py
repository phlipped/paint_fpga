from migen import *
from edge_detect import EdgeDetect

class Spi(Module):
  '''Basic Spi Module.

  Signal Args:
    spi_clk: Signal 1 x in
    ss: Signal 1 x in, Acive LOW
    miso: Signal 1 x out
    mosi: Signal 1 x in
    data_in: Signal n x in/out
    data_in_ready: Signal 1 x in/out (set internally when a full word has been received. The use of this Spi Module is needs to clear data_in_ready when they've read the word from data_in

  Not Yet implemented:
    miso: Signal 1 x out
    data_out: Signal n x out
    data_out_ready: Signal 1 x out
  '''
  def __init__(self, spi_clk, ss, miso, mosi, data_in, data_in_ready):
    word_size = len(data_in)
    bit_count = Signal(max=word_size) # Count number of bits transferred
    input_buf = Signal(word_size)

    spi_clk_rising = Signal()
    self.submodules.spi_edge = EdgeDetect(spi_clk, spi_clk_rising)

    # When ss is low (active), that's when we do our work.
    # Otherwise, ss is high, so we continuously assert a 'reset' state.
    self.sync += If(~ss,
                    If(spi_clk_rising,
                       # Count the number of bits we've received
                       If(bit_count == word_size - 1, # Wrap around when we hit the top
                          bit_count.eq(0),
                          data_in.eq(input_buf), # Copy the input_buf to the externally-exposed <data_in> register
                          data_in_ready.eq(1)  # Reader of data_in is expected to clear data_in_ready after they've read the value from data_in.
                       ).Else(
                           bit_count.eq(bit_count + 1)
                       ),

                       # Shift the data into the input_buf
                       input_buf.eq(Cat(mosi, input_buf[:-1])),
                    )
                    ).Else (  # ss is high, so we should just reset everything.
                        # FIXME try to re-use built-in reset to achieve this?
                        # which would automatically propogate to our submodules (right?)
                        # FIXME reset our edge_detect module
                        input_buf.eq(0),
                        data_in_ready.eq(0),
                        data_in.eq(0),
                        bit_count.eq(0),
                    )

