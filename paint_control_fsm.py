import functools
import operator

from nmigen import *

from motor_enable import MotorEnable
from pwm import Pwm
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

class PaintControlFSM(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()

        # == control ==:
        # Writeable
        #   0  : Reset
        #   1-2: Mode - 01 is dispensing, 10 is homing, 11 is illegal
        #   3-7: Undefined
        self.control = Signal(8)

        # == reset ==
        # Just identifies one field of control register.
        # There's a better way to do this - a "layout" or something?
        # I just don't know how to do it yet
        self.reset = Signal()
        m.d.comb += self.reset.eq(self.control[0])

        # == error ==
        # Read-only from outside
        # In error state, this is populated with a value
        # It is cleared when entering READY state

        # == colours_in ==
        # Writeable
        # Collection of registers where steps for each colour can be specified
        self.colours_in = []

        # == colours ==
        # Read-only from outside
        # Collection of registers used to update the remaining steps for each
        # colour
        self.colours = []

        # motor_enables
        #
        # Collection of 'motor_enable' submodules to manage the enable logic for
        # each motor
        self.motor_enables = []

        # Populate colours_in, colours and motor_enables
        for i in range(5):
            self.colours_in.append(Signal(32))
            self.colours.append(Signal(32))
            motor_enable = MotorEnable()
            self.motor_enables.append(motor_enable)
            m.submodules += motor_enable

        # Pulse generator used to drive the step signal
        pulser = Pwm(16)
        m.submodules.pulser = pulser
        m.d.comb += pulser.invert.eq(1)

        # Clock domain for "step_signal".
        # In READY state, this domain is synced to the 'sync' clock domain so
        # that various step-related registers are populated from sync domain.
        # Then, when stepping actually starts, the step_signal is driven from
        # the pulser module.
        step_signal = ClockDomain('step_signal')
        m.domains += step_signal

        # The FSM just reacts to the state of various registers being
        # written to asynchronously by the SPI module
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
                with m.If(self.reset == 0):
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
                # If the mode bits == 'DISPENSING', go to dispensing mode
                # If the mode bits == 'HOMING', go to homing mode

                m.d.comb += step_signal.clk.eq(ClockSignal('sync'))

                # FIXME do this properly - ie calculate values appropriately or something
                # load some basic values into pwm module
                m.d.sync += [
                    pulser.top.eq(100),
                    pulser.match.eq(16),
                ]

                # Assign the incoming color values to corresponding writable registers
                # Do this on the step clock, which is currently bound to the sync
                # clock anyway
                m.d.step_signal += [o.eq(i) for i, o in zip(self.colours_in, self.colours)]

                with m.If(self.reset):          # If CANCEL bit is set, go back to START
                    m.next = "START"
                with m.Else():                  # Otherwise, normal case ...
                    with m.Switch(self.control[1:3]):
                        with m.Case(0b01):
                            m.next = "DISPENSING_PREP"
                        with m.Case(0b10):
                            m.next = "HOMING"
                        with m.Case(0b11):      # Illegal case - go to error state
                            # FIXME set error code
                            m.next = "ERROR"
                        with m.Default():       # Case 00 - means don't do anything
                            pass

            with m.State("DISPENSING_PREP"):
                # Switch step_signal clock source to the pulser output
                m.d.comb += step_signal.clk.eq(pulser.o)

                # Turn on the enable line of any motor which has non-zero steps
                for i, e in enumerate(self.motor_enables):
                    with m.If (self.colours[i] != 0):
                        m.d.sync += e.enable_i.eq(1)
                m.next = "DISPENSING"

            # DISPENSE
            # next states are
            # - READY
            # - ERROR
            with m.State("DISPENSING"):
                # continue driving step_signal from pulser module
                m.d.comb += step_signal.clk.eq(pulser.o)

                # start the pulser module
                m.d.sync += pulser.active.eq(1)

                # Enable the motors for colours that have steps,
                # and turn them off when the step count for the colour hits 0
                for i, c in enumerate(self.colours):
                    with m.If(c == 0):
                        # Wait until pulser is zero.
                        # This is a bit hacky - ideally we should wait for 1us
                        # after the pulse goes low. But I'm guessing the stepper
                        # motor driver won't care - it's probably already done
                        # the step after the rising edge, right?
                        with m.If(pulser.o == 0):
                            m.d.sync += self.motor_enables[i].enable_i.eq(0)
                    with m.Else():
                        m.d.sync += self.motor_enables[i].enable_i.eq(1)

                with m.If(self.reset):
                    m.next = "START"

                with m.Else():
                    # If a motor went wrong, then go to ERROR
                    # determine if any limits were hit - store result in any_limit_hit
                    limit_hits = [self.motor_enables[i].limit_for_direction & self.colours[i] != 0
                                  for i in range(len(self.motor_enables))]
                    any_limit_hit = functools.reduce(operator.or_, limit_hits)
                    with m.If(any_limit_hit):
                        # FIXME set error code
                        m.next = "ERROR"

                    with m.Else(): # Normal case here
                        for c in self.colours:
                            with m.If(c != 0):
                                m.d.step_signal += c.eq(c-1)

                        # If all colours are 0, go to DONE
                        with m.If(functools.reduce(operator.or_, self.colours) == 0):
                            # wait for final pulse to compete
                            with m.If(pulser.o == 0):
                                m.next = "DONE"

            # HOME
            # next states are
            # - READY
            # - ERROR
            with m.State("HOMING"):
                with m.If(self.reset):
                    m.next = "START"

                with m.Else():
                    pass

            # DONE
            # wait until a reset is asserted before continuing.
            # next states are:
            # - START
            with m.State("DONE"):
                with m.If(self.reset):     # If CANCEL bit is set, go back to START
                    m.next = "START"

            # ERROR
            # Entered when unexpected error state occurs
            # e.g. protocol error, hardware error
            # next states are
            # - START
            # FIXME could probably just be folded into "DONE" state?
            with m.State("ERROR"):
                with m.If(self.reset):
                    m.next = "START"

        return m
