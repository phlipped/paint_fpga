from nmigen import *

class MotorEnable(Elaboratable):
    def __init__(self, is_test=False):
        self.limit_top = Signal() # 1 means it's been hit, 0 means not hit
        self.limit_bottom = Signal() # 1 means it's been hit, 0 means ok
        self.direction = Signal() # 1 means 'down', 0 means 'up'
        self.enable_i = Signal()
        self.enable_o = Signal()
        self.is_test = is_test
        if is_test:
          self.dummy = Signal()

    def elaborate(self, platform):
        m = Module()
        if self.is_test:
          with m.If(self.dummy == 1):
              m.d.sync += self.dummy.eq(0)
          with m.Else():
              m.d.sync += self.dummy.eq(1)

        with m.If(self.direction == 1):  # direction is down
            with m.If(self.limit_bottom == 1):
                m.d.comb += self.enable_o.eq(0)
            with m.Else():
                m.d.comb += self.enable_o.eq(self.enable_i)

        with m.Else():  # direction is up
            with m.If(self.limit_top == 1):
                m.d.comb += self.enable_o.eq(0)
            with m.Else():
                m.d.comb += self.enable_o.eq(self.enable_i)
        return m
