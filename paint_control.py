from nmigen import *

from motor_enable import MotorEnable
'''
Controlled by a number of configuation and status registers.
These are readable/writable by SPI

Each register is 8 bits

Registers 0 through 24 are 5 lots of 5-register modules relating to the motors
0: Motor Step Count Lower
1: Motor Step Count Higher
2: Motor Status - limit_top, limit_bottom

25: General Control register
25.0: start/stop - set 0 to stop things, set 1 to make things go
25.1: 0 = Dispense mode, 1 = Home mode
25.2: Clear error state - return to Ready state

26: Status Register (Read only)
26.0: Active flag - are things moving right now?
26.1: Current mode: 0 = Dispense, 1 = Home mode
26.2: In Error
26.3: Error type - 0 Protocol error, 1 Hardware error

27: Max Speed control register
28: Ramp up speed control register

'''

class PaintControl(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()

        ro_registers = []
        rw_registers = []
        # 0  : Reset
        # 1-2: Mode - 01 is dispensing, 10 is homing, 11 is illegal
        # 3-7: Undefined
        self.control = Signal(8)
        self.reset = Signal()
        m.d.comb += self.reset.eq(self.control[0])
        self.colours_in = []
        self.colours = []
        self.motor_enables = []
        for i in range(5):
            self.colours_in.append(Signal(32))
            self.colours.append(Signal(32))
            motor_enable = MotorEnable()
            self.motor_enables.append(motor_enable)
            m.submodules += motor_enable

        with m.FSM() as fsm:
            # In all states, at any time, if 'reset' bit is set, go to "START" state
            # How does this work in terms of determining which state to go to next?
            # Can we make this a global?
            # Like, if "reset" gets asserted at the same time as "DISPENSING",
            # which state will it actually go to?
            # Could put them in different registers - that way they can't be
            # asserted at the same time? Seems a bit like a cop out, though, and
            # arguably a landmine for the future.

            # not sure if needed?
            # performs a POST?
            # next states
            # - READY -> if POST SUCCEEDS
            # - ERROR -> if POST fails (e.g. end stop switches are bad)
            with m.State("START"):
                # FIXME actually implement POST - e.g. check the limit switches are happy
                with m.If(self.control[0] == 0):
                    m.next = "READY"

            # READY
            # state where various values can be set - e.g.
            # set the step count for each motor when dispensing
            # Or select which motors to home when homing (and which direction)
            # Could probably re-use the same registers for both these
            # modes. e.g. when homing, a non-zero value in a colour's step
            # register indicates that the colour should be homed.
            # next states are
            # - DISPENSING
            # - HOMING
            # - ERROR
            with m.State("READY"):
                # We just react to SPI commands
                # If the mode bits == 'DISPENSING', go to dispensing mode
                # If the mode bits == 'HOMING', go to homing mode
                with m.If(self.control[0]):
                    m.next = "START"

                with m.Else():
                    with m.Switch(self.control[1:3]):
                        with m.Case(0b01):
                            m.next = "DISPENSING"
                        with m.Case(0b10):
                            m.next = "HOMING"
                        with m.Case(0b11):
                            # Illegal case - go to error state
                            m.next = "ERROR"
                        with m.Default():
                            # Case 00 - means don't do anything
                            pass
                    # Assign the incoming color values to corresponding writable registers
                    m.d.sync += [self.colours[i].eq(self.colours_in[i]) for i in range(5)]

            # DISPENSE
            # next states are
            # - READY
            # - ERROR
            with m.State("DISPENSING"):
                with m.If(self.control[0]):
                    m.next = "START"

                with m.Else():
                    # If there is an error from the motor module
                    #     go to ERROR
                    # Else
                    #     for each colour register ...
                    #     If all counts are at zero
                    #         Go to state START
                    pass

            # HOME
            # next states are
            # - READY
            # - ERROR
            with m.State("HOMING"):
                with m.If(self.control[0]):
                    m.next = "START"

                with m.Else():
                    pass


            # ERROR
            # Entered when unexpected error state occurs
            # e.g. protocol error, signal error
            # Hitting end stops and thus terminating a normal dispense event
            # is not considered an error.
            # next states are
            # - READY
            with m.State("ERROR"):
                with m.If(self.control[0]):
                    m.next = "START"

                with m.Else():
                    pass

        return m
