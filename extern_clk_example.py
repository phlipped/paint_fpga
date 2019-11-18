from nmigen import *
from nmigen_boards import tinyfpga_bx, atlys

class SubMod(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        count = Signal(8)
        m.d.sync += count.eq(count + 1)
        return m

class SubModBoard(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.sub_mod  = SubMod()
        return m

if __name__ == "__main__":
    plat = tinyfpga_bx.TinyFPGABXPlatform()
    # plat = atlys.AtlysPlatform()
    plat.build(SubModBoard(), do_program=False)
