# paint_control mediates transfer of information between the spi interface
# and the fsm core that is doing the work.
# Not sure it actually does anything other than join those other two modules together
from nmigen import *

class PaintControl(Elaboratable):
    """
THE FOLLOWING DOCSTIRNG IS INCORRECT - ENERALLY IGNORE IT, AND RECREATE PROPERLY
--------------------------------
Controlled by a number of configuation and status registers.
These are readable/writable by SPI

Each register is 8 bits

Registers 0 through 24 are 5 lots of 5-register modules relating to the motors
0: Motor Step Count Lower
1: Motor Step Count Higher
2: Motor Status - limit_top, limit_bottom

25: General Control register
25.0: start/stop - set 0 to stop things, set to 1 to make things go
25.1: 0 = Dispense mode, 1 = Home mode
25.2: Clear error state - return to Ready state

26: Status Register (Read only)
26.0: Active flag - are things moving right now?
26.1: Current mode: 0 = Dispense, 1 = Home mode
26.2: In Error
26.3: Error type - 0 Protocol error, 1 Hardware error

27: Max Speed control register
28: Ramp up speed control register
-------------------------------
    """
    def __init__(self):
        self.spi_clk = Signal()
        self.ss = Signal()
        self.mosi = Signal()
        self.miso = Signal()

    def elaborate(self, platform):
        m = Module()

        fsm = PaintControlFSM()
        m.submodules += fsm

        regs = []
        # 0 -> control
        regs.append((fsm.control, 1))

        # Add colours_in to regs as 4 8-bit writable registers
        # 1-4 -> colour0_in
        # 5-8 -> colour1_in
        # 9-12 -> colour2_in
        # 13-16 -> colour3_in
        # 17-20 -> colour4_in
        for i in range(5):    # do this 5 times - one for each colour
            for j in range(4):
                regs.append(fsm.colours_in[j*8:j*8+8], 1)

        # Same deal for read-only colours registers
        # 21-24 0
        # 25-28 1
        # 29-32 2
        # 33-36 3
        # 37-40 4
        for i in range(5):    # do this 5 times - one for each colour
            for j in range(4):
                regs.append(fsm.colours[j*8:j*8+8], 0)

        # FIXME add in the motor signals as read-only registers
        # FIXME create and add a status register to the mix


        spi_reg_if = SpiRegIf(regs)
        spi_reg_if.spi_clk = self.spi_clk
        spi_reg_if.ss = self.ss
        spi_reg_if.mosi = self.mosi
        spi_reg_if.miso = self.miso
