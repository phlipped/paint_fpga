# Misc thoughts and stuff
- Ideally create small, testable modules.
- e.g. with SPI, make a shift register module, then add in things like
  slave-select and reset, then add in things like bit counters and 'ready' flags
  Then wrap that all in FFSynchronizers to get the data in/out.
  Probably want to think about the design of the SPI interface (from the rest of
  the FPGA first).

# CHANGE LOG

## 2019-12-02
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
