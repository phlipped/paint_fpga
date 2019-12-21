from nmigen import *

class MotorEnable(Elaboratable):
    def __init__(self, is_test=False):
        self.limit_top = Signal() # 1 means it's been hit, 0 means not hit
        self.limit_bottom = Signal() # 1 means it's been hit, 0 means ok
        self.limit_for_direction = Signal() # Represents the limit in the relevant direction
        self.direction = Signal() # 1 means 'down', 0 means 'up'
        self.enable_i = Signal() # incoming enable signal from paint controller
        self.enable_o = Signal() # outgoing enable signal to motors
        self.is_test = is_test # create a dummy signal so that we have a clock
        if is_test:
          self.dummy = Signal()

    def elaborate(self, platform):
        m = Module()
        if self.is_test:
            m.d.sync += self.dummy.eq(~self.dummy)

        with m.If(self.direction == 1): # 1 means down
            m.d.comb += self.limit_for_direction.eq(self.limit_bottom)
        with m.Else():
            m.d.comb += self.limit_for_direction.eq(self.limit_top)

        with m.If(self.limit_for_direction == 1):
            m.d.comb += self.enable_o.eq(0)
        with m.Else():
            m.d.comb += self.enable_o.eq(self.enable_i)

        return m
