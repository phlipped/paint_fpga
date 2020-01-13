# paint_control mediates transfer of information between the spi interface
# and the fsm core that is doing the work.
# Not sure it actually does anything other than join those other two modules together
from nmigen import *

from paint_control_fsm import *
from spi import *


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

        self.fsm = fsm = PaintControlFSM()
        m.submodules += fsm

        read_regs = Array()
        write_regs = Array()
        # 0 -> control
        read_regs.append(fsm.control)
        write_regs.append(fsm.control)

        # Add colours_in to regs as 4 8-bit writable registers
        # 1-4 -> colour0_in
        # 5-8 -> colour1_in
        # 9-12 -> colour2_in
        # 13-16 -> colour3_in
        # 17-20 -> colour4_in
        for i in range(5):    # do this 5 times - one for each colour
            for j in range(4):
                read_regs.append(fsm.colours_in[i][j*8:j*8+8])
                write_regs.append(fsm.colours_in[i][j*8:j*8+8])

        # Same deal for read-only colours registers
        # 21-24 0
        # 25-28 1
        # 29-32 2
        # 33-36 3
        # 37-40 4
        for i in range(5):    # do this 5 times - one for each colour
            for j in range(4):
                read_regs.append(fsm.colours[i][j*8:j*8+8])

        # FIXME add in the motor signals as read-only registers
        # FIXME create a status register in paint_control_fsm, then link to it here

        spi_reg_if = SpiRegIf(read_regs, write_regs)
        spi_reg_if.spi_clk = self.spi_clk
        spi_reg_if.ss = self.ss
        spi_reg_if.mosi = self.mosi
        spi_reg_if.miso = self.miso
        m.submodules += spi_reg_if

        return m
