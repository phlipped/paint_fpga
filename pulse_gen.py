from nmigen import *

class PulseGen(Elaboratable):
    def __init__(self, width=16):
        self.pulse = Signal()  # output
        self._pulse = Signal()
        self.top = Signal(width)  # max value of counter
        self.match = Signal(width)  # value at which to turn pulse on
        self.counter = Signal(width)  # underlying counter - read only
        self.active = Signal()  # whether to run the pulse generator - set to 0 to deactivate and set counter to 1
        self.invert = Signal() # Start high then go low

        self.match2 = Signal(width)
        self.top2 = Signal(width)
        self.active2 = Signal()
        self.invert2 = Signal()

    def elaborate(self, platform):
        m = Module()

        # overcome bug in nmigen
        m.d.comb += [
            self.match2.eq(self.match),
            self.top2.eq(self.top),
            self.active2.eq(self.active),
            self.invert2.eq(self.invert),
        ]

        with m.If(self.active):
            m.d.comb += self.pulse.eq(self.invert ^ self._pulse)
            with m.If(self.counter == self.top):
                m.d.sync += [
                    self.counter.eq(0),
                    self._pulse.eq(0),
                ]
            with m.Else():
                m.d.sync += self.counter.eq(self.counter + 1)
                with m.If(self.counter == self.match):
                        m.d.sync += self._pulse.eq(1)

        with m.Else():
            m.d.sync += self.counter.eq(0)
            m.d.comb += self.pulse.eq(0)

        return m
