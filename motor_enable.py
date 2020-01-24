from nmigen import *

class MotorEnable(Elaboratable):
    def __init__(self):
        self.limit_top = Signal() # 1 means it's been hit, 0 means not hit
        self.limit_bottom = Signal() # 1 means it's been hit, 0 means ok
        self.limit_for_direction = Signal() # multiplex between the two limit signals based on the value of direction
        self.direction = Signal() # 1 means 'down', 0 means 'up'
        self.enable_i = Signal() # incoming enable signal from paint controller
        self.enable_o = Signal() # outgoing enable signal to motors

        # For testing purposes only
        self.dummy = Signal()
        self.enable_i2 = Signal()
        self.limit_top2 = Signal()
        self.limit_bottom2 = Signal()
        self.direction2 = Signal()

    def elaborate(self, platform):
        m = Module()

        # For testing purposes only
        m.d.sync += self.dummy.eq(~self.dummy)
        m.d.comb += [
            self.enable_i2.eq(self.enable_i),
            self.limit_top2.eq(self.limit_top),
            self.limit_bottom2.eq(self.limit_bottom),
            self.direction2.eq(self.direction),
        ]

        with m.If(self.direction == 1): # 1 means down
            m.d.comb += self.limit_for_direction.eq(self.limit_bottom)
        with m.Else():
            m.d.comb += self.limit_for_direction.eq(self.limit_top)

        with m.If(self.limit_for_direction == 1):
            m.d.comb += self.enable_o.eq(0)
        with m.Else():
            m.d.comb += self.enable_o.eq(self.enable_i)

        return m
