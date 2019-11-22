# What just happened
- creating this branch to work on the basic skeleton of files
- created some initial skeleton files that I think will be necessary
- filled out platform.py (ie defined the input/outputs and how they map to the
  tinyfpga_bx pins. The actual mapping will almost certainly need to be updated)
  - has been tested by importing the file and instantiating the class

# What happens next
- Fill out the a skeleton for spi.py and motor.py
  - define the IO interface so they it can be used by other modules
  - although getting SPI cross domain clocking should probably be worked out
    first
    - UPDATE: There's been a successful test of external clock as well as
    clock domain crossing - over in cdc_testing branch. Still a small amount
    of work to do before that line of investigation can be closed off.
- Start working on paint_control.py, using the spi.py and motor.py modules
