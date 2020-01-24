# paint_control mediates transfer of information between the spi interface
# and the fsm core that is doing the work.
# Not sure it actually does anything other than join those other two modules together
from nmigen import *

from paint_control_fsm import *
from spi import *


class PaintControl(Elaboratable):
    """
Controlled by a number of configuation and status registers.
These are readable/writable by SPI

Each register is 8 bits

R0 is control register with following bits:
0  : reset
1-2: mode - 00 means nothing, 10 means 'dispense', 01 means 'home' and 11 is illegal
3  : direction - 0 means down, 1 means up
4-7: <reserved>

R1 and R2 are two halves 16-bit "TOP" register of PWM module
Controls the maximum value of PWM counter that controls step rate

R3 and R4 are two halves of 16-bit "MATCH" register of PWM module
Controls when the PWM signal switches from high to low

R5-R8 are for 32 bit color[0] desired step count
R9-R12 " " " " " " " " " " 1 " " " " " " " " " "
R13-R16  " " " " " " " " " 2 " " " " " " " " " "
R17-R20  " " " " " " " " " 3 " " " " " " " " " "
R21-R24  " " " " " " " " " 4 " " " " " " " " " "

R25-R44 same deal, 5 lots of 4 byte registers that show CURRENT step count. READ ONLY
-------------------------------
    """
    def __init__(self):
        self.spi_clk = Signal()
        self.ss = Signal()
        self.mosi = Signal()
        self.miso = Signal()
        self.motor_signals = Array()
        for i in range(5):
            r = Record(layout=[
                ("enable_o", 1),
                ("limit_top", 1),
                ("limit_bottom", 1),
            ])
            self.motor_signals.append(r)
        self.steps = Signal()
        self.direction = Signal()

    def elaborate(self, platform):
        m = Module()

        self.fsm = fsm = PaintControlFSM()
        m.submodules += fsm

        dummy_write = Signal(8)

        # wire up the motor enable signals
        for i, r in enumerate(self.motor_signals):
            fsm.motor_enables[i].enable_o = r.enable_o
            fsm.motor_enables[i].limit_top = r.limit_top
            fsm.motor_enables[i].limit_bottom = r.limit_bottom

        # wire up the step signal and direction signal
        self.fsm.steps = self.steps
        self.fsm.control.direction = self.direction

        read_regs = Array()
        write_regs = Array()

        # reg 0 -> status
        # read only
        status_as_signal = Cat(
            fsm.status.fsm_state,
            fsm.status.error_code,
        )
        read_regs.append(status_as_signal)
        write_regs.append(dummy_write)

        # reg 1 -> control
        # FIXME not sure why I have to do make a control_as_signal thing, but trying to use
        # fsm.control directly as a register in an Array doesn't work - a Record
        # can't be used as a key in value collections. I'm not sure why it needs
        # to be a key - I thought it was just being a value - but either way
        # that's the error I get.
        control_as_signal = Cat(
            fsm.control.reset,
            fsm.control.mode,
            fsm.control.direction,
            fsm.control.reserved
        )

        read_regs.append(control_as_signal)
        write_regs.append(control_as_signal)

        read_regs.append(fsm.pulser.top[0:8])
        read_regs.append(fsm.pulser.top[8:16])
        write_regs.append(fsm.pulser.top[0:8])
        write_regs.append(fsm.pulser.top[8:16])

        read_regs.append(fsm.pulser.match[0:8])
        read_regs.append(fsm.pulser.match[8:16])
        write_regs.append(fsm.pulser.match[0:8])
        write_regs.append(fsm.pulser.match[8:16])

        # Add colours_in to regs as 4 8-bit writable registers
        # 6-9 -> colour0_in
        # 10-13 -> colour1_in
        # 14-17 -> colour2_in
        # 18-21 -> colour3_in
        # 22-25 -> colour4_in
        for i in range(5):
            for j in range(4):
                read_regs.append(fsm.colours_in[i][j*8:j*8+8])
                write_regs.append(fsm.colours_in[i][j*8:j*8+8])

        # Same deal for read-only colours registers
        # 26-29 0
        # 30-33 1
        # 34-37 2
        # 38-41 3
        # 42-45 4
        for i in range(5):    # do this 5 times - one for each colour
            for j in range(4):
                read_regs.append(fsm.colours[i][j*8:j*8+8])
                write_regs.append(dummy_write)

        # FIXME add in the motor signals as read-only registers
        # FIXME create a status register in paint_control_fsm, then add it in as a read-only register here

        spi_reg_if = SpiRegIf(read_regs, write_regs)
        # wire up the spi signals
        spi_reg_if.spi_clk = self.spi_clk
        spi_reg_if.ss = self.ss
        spi_reg_if.mosi = self.mosi
        spi_reg_if.miso = self.miso
        m.submodules += spi_reg_if

        return m
