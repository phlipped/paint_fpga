from nmigen import *

class PulseGen(Elaboratable):
    def __init__(self, width=16):
        self.pulse = Signal()
        self.top = Signal(width)
        self.match = Signal(width)
        self.counter = Signal(width)
        self.active = Signal()

        self.match2 = Signal(width)
        self.top2 = Signal(width)
        self.active2 = Signal()

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.match2.eq(self.match),
            self.top2.eq(self.top),
            self.active2.eq(self.active),
        ]

        with m.If(self.active):
            with m.If(self.counter == self.top):
                m.d.sync += [
                    self.counter.eq(0),
                    self.pulse.eq(0),
                ]
            with m.Else():
                m.d.sync += self.counter.eq(self.counter + 1)
                with m.If(self.counter == self.match):
                        m.d.sync += self.pulse.eq(1)

        with m.Else():
            m.d.sync += self.counter.eq(0)

        return m
