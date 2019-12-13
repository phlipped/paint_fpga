# Current status
- spi core module basically works (I think) and has tests.
- motor_enable contains the combinatorial logic to handle a single motor and
the associated limit switches and enable line

## Up next
- Perhaps: Make a more advanced SPI module that actually interprets a protocol.
Though this might require actually having some central logic that the SPI will
interact with - e.g. addresses/registers to read/write via SPI.
- Make the step-count logic unit. In particular, the timing and smooth-start
parts.

# CHANGE LOG

## 2019-12-13
### What just happened
- Merg

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
