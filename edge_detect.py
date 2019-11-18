from nmigen import *
from nmigen.cli import main

class EdgeDetect(Elaboratable):
    '''EdgeDetect Module.

    Generates a pulse when a rising and/or falling edge is detected on some
    input signal.

    Edge detection is implemented by forwarding the input signal through a
    shift register and comparing the two bits at the 'end' of the shift register
    to 0b01 (rising) or 0b10 (falling).

    The output pulse will be delayed behind the original edge - the delay is
    proportional to the buffer depth, The average delay (in
    clock-widths) can be calculated with: (buf_depth - 1) + 0.5

    Args:
      rising: Whether to create a signal on the rising edge
      falling: Whether to create a signal on the falling edge
      buf_depth: Depth of shift register buffer, default 3
    '''
    def __init__(self, rising=False, falling=False, buf_depth=3):
        self.sig = Signal()
        self.rising = Signal() if rising else None
        self.falling = Signal() if falling else None

        ###

        self.buf = Signal(buf_depth)

    def elaborate(self, platform):
        m = Module()
        m.d.sync += self.buf.eq(Cat(self.sig, self.buf[0:-1]))
        if self.rising is not None:
            m.d.sync += self.rising.eq(self.buf[-2:] == 0b01)
        if self.falling is not None:
            m.d.sync += self.falling.eq(self.buf[-2:] == 0b10)
        return m

if __name__ == '__main__':
    ed = EdgeDetect(rising=True)
    main(ed, ports=[ed.sig, ed.rising])
