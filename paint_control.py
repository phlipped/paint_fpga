from nmigen import *

from spi import SpiRegIf

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
        spi_if = SpiInterface()

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
            # performs a POST
            # next states
            # - READY -> if POST SUCCEEDS
            # - ERROR -> if POST fails (e.g. end stop switches are bad)
            with m.state("START"):
                # FIXME actually implement POST - e.g. check the limit switches are happy
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
            with m.state("READY"):
                # We just react to SPI commands
                # If the mode bits == 'DISPENSING', go to dispensing mode
                # If the mode bits == 'HOMING', go to homing mode
                pass
            # DISPENSE
            # next states are
            # - READY
            # - ERROR
            with m.state("DISPENSING"):
                pass

            # HOME
            # next states are
            # - READY
            # - ERROR
            with m.state("HOMING"):
                pass

            # ERROR
            # Entered when unexpected error state occurs
            # e.g. protocol error, signal error
            # Hitting end stops and thus terminating a normal dispense event
            # is not considered an error.
            # next states are
            # - READY
            with m.state("ERROR"):
                pass

        return m
