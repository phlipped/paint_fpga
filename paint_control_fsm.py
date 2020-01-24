import functools
import operator

from nmigen import *

from motor_enable import MotorEnable
from pwm import Pwm

FSM_STATE_ID = {
    'START': 0,
    'READY': 1,
    'DISPENSING_PREP': 2,
    'DISPENSING': 5,
    'HOMING': 3,  # Not confirmed that this is thae same as in gtkwave file
    'DONE': 6,
    'ERROR': 4,   # Not confirmed that this is thae same as in gtkwave file
}

class PaintControlFSM(Elaboratable):
    def __init__(self):
        # == status ==
        # Read Only
        self.status = Record(layout=[
            ("fsm_state", 4),
            ("error_code", 4),
        ])

        # == control ==:
        # Writeable
        self.control = Record(layout=[
            ("reset", 1),
            ("mode", 2),  # FIXME clear up the endianness
            ("direction", 1),  # 0 means down, 1 means up FIXME not yet implemented
            ("reserved", 4),
        ])

        # == error ==
        # Read-only
        # In error state, this is populated with a value
        # It is cleared when entering READY state
        # FIXME implement

        # == colours_in ==
        # Writeable
        # Collection of registers where steps for each colour can be specified
        self.colours_in = []

        # == colours ==
        # Read-only from outside
        # Collection of registers used to update the remaining steps for each
        # colour
        self.colours = []

        # == motor_enables ==
        # Collection of 'motor_enable' submodules to manage the enable logic for
        # each motor
        self.motor_enables = []

        # Populate colours_in, colours and motor_enables
        for i in range(5):
            self.colours_in.append(Signal(32))
            self.colours.append(Signal(32))
            motor_enable = MotorEnable()
            self.motor_enables.append(motor_enable)

        self.steps = Signal()
        self.pulser = Pwm(16)


    def elaborate(self, platform):
        m = Module()

        for i in range(5):
            m.submodules += self.motor_enables[i]
            m.d.comb += self.motor_enables[i].direction.eq(self.control.direction)

        # Pulse generator used to drive the step signal

        self.pulser.o = self.steps
        m.submodules.pulser = self.pulser
        m.d.comb += self.pulser.invert.eq(1)

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
                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['START'])
                m.d.sync += self.pulser.active.eq(0)
                with m.If(self.control.reset == 0):
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

                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['READY'])
                m.d.comb += step_signal.clk.eq(ClockSignal('sync'))

                # FIXME do this properly - ie calculate values appropriately or something
                # load some basic values into pwm module
                # m.d.sync += [
                #    pulser.top.eq(100),
                #    pulser.match.eq(16),
                # ]

                # Assign the incoming color values to corresponding writable registers
                # Do this on the step clock, which is currently bound to the sync
                # clock anyway
                m.d.step_signal += [o.eq(i) for i, o in zip(self.colours_in, self.colours)]

                with m.If(self.control.reset):          # If CANCEL bit is set, go back to START
                    m.next = "START"
                with m.Else():                  # Otherwise, normal case ...
                    with m.Switch(self.control.mode):
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
                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['DISPENSING_PREP'])
                m.d.comb += step_signal.clk.eq(self.pulser.o)

                # Turn on the enable line of any motor which has non-zero steps
                for i, e in enumerate(self.motor_enables):
                    with m.If(self.colours[i] != 0):
                        m.d.sync += e.enable_i.eq(1)
                m.next = "DISPENSING"

            # DISPENSING
            # next states are
            # - START
            # - ERROR
            # - DONE
            with m.State("DISPENSING"):
                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['DISPENSING'])
                # continue driving step_signal from pulser module
                m.d.comb += step_signal.clk.eq(self.pulser.o)

                # start the pulser module
                m.d.sync += self.pulser.active.eq(1)

                with m.If(self.control.reset):
                    m.next = "START"

                with m.Else():
                    # Disable motors for colours that reach 0
                    for i, c in enumerate(self.colours):
                        with m.If(c == 0):
                            # Wait until pulser is zero.
                            # This is a bit hacky - ideally we should wait for 1us
                            # after the pulse goes low. But I'm guessing the stepper
                            # motor driver won't care - it's probably already done
                            # the step after the rising edge, right?
                            with m.If(self.pulser.o == 0):
                                m.d.sync += self.motor_enables[i].enable_i.eq(0)
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
                            with m.If(self.pulser.o == 0):
                                m.next = "DONE"

            # HOME
            # next states are
            # - READY
            # - ERROR
            with m.State("HOMING"):
                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['HOMING'])
                with m.If(self.control.reset):
                    m.next = "START"

                with m.Else():
                    pass

            # DONE
            # wait until a reset is asserted before continuing.
            # next states are:
            # - START
            with m.State("DONE"):
                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['DONE'])
                # Turn off the pulser
                m.d.sync +=self.pulser.active.eq(0)
                with m.If(self.control.reset):     # If CANCEL bit is set, go back to START
                    m.next = "START"

            # ERROR
            # Entered when unexpected error state occurs
            # e.g. protocol error, hardware error
            # next states are
            # - START
            # FIXME could probably just be folded into "DONE" state?
            with m.State("ERROR"):
                m.d.sync += self.status.fsm_state.eq(FSM_STATE_ID['ERROR'])
                with m.If(self.control.reset):
                    m.next = "START"

        return m
