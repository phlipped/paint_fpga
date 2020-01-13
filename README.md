# CHANGE LOG

## 2020-01-14
- Wire up various signals from paint_control to paint_control_fsm.
- Next step is probably to create a 'board', wire up the board to the paint_control
  module, and try to write it to the TinyFPGA


## 2020-01-13
- Simple end to end test completed. It largely seems to work? Gosh!
- Need to sort out the endianness of various registers (e.g. colour steps registers)
- Meaning of direction (1 is up, 0 is down?). Doesn't even support setting the
  direction at this stage.

## 2020-01-13
- Basic top-level module is working that joins spi to paint control fsm
- Needed to split the regs into read regs and write regs, because otherwise
there was a conflict about how the read regs were being driven (The app logic
  prevented the read regs from being driven, but the compiler has no way of knowing
  that and as far as it can tell they could potentially get driven because they
  were in the same array as writable registers)

## 2019-12-28 23:00
- Expanded the tests for paint_control - can actualy get it into and out of dispensing mode.
- some bug fixes - previous commit is broken. Can't remember what.

## 2019-12-28 21:00
### What just happened
- building out the main paint control module, including ...
 - pulse gen module
 - array of motor_enable modules
 - building finite state machine
 - wrangling with driving the step registers from different clock sources
  - the solution appears to be to change the clock source for the domain,
  - but this needs to be tested. In particular, I don't want to see spurious steps during the cutover period from one clock source to another.

## 2019-12-13
### What just happened
- Not sure

### What happens next
- Not sure

### What just happened
- Overhauled SPI module to use a dedicated clock domain - removed the edge
detect stuff.
- Overhauled tests - required upgrade to latest nmigen simulator that overcomes
some deficiencies in the old simulator.

### What happens next
- Not sure ... I had an idea once, and then I forgot. I feel like it was
something to do with SPI though.

## 2019-12-02
### What just happened
- Created basic motor controller combinatorial logic unit, with basic test

### What happens next
- Create a battery of motor enable controllers?

### What just happened
- Merged SPI work (see tag archive/spi_core_developemnt)

### What happens next
- Build out the module parts that arethat's going to interact with SPI
 - Might require making a state machine bizzo?
- Build out the module parts that do the combinatorial logic (ie the motor_controller
  parts of the device)

## 2019-11-XX
### What just happened
- creating this branch to create a skeleton structure.
- created some initial skeleton files that I think will be necessary
- filled out platform.py (ie defined the input/outputs and how they map to the
  tinyfpga_bx pins. The actual mapping will almost certainly need to be updated)
  - has been tested by importing the file and instantiating the class

### What happens next
- Fill out the a skeleton for spi.py and motor.py
  - define the IO interface so they it can be used by other modules
  - although getting SPI cross domain clocking should probably be worked out
    first
    - UPDATE: There's been a successful test of external clock as well as
    clock domain crossing - over in cdc_testing branch. Mostly just need to
    do a real-world test
- Start working on paint_control.py, using the spi.py and motor.py modules
