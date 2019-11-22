# What's happening here
Experimenting with all the custom clock stuff for the SPI module
 - driving a clock from an external GPIO
 - passing signals to some other clock domain
  - does it matter which one's faster?

# What just happened
## Key Insight
need to use "ClockSignal(<clock_domain>)" to get the relevant
clock, and bind it to some other signal in a m.d.comb block - look inside
ext_counter.py for hints.

## What's here?
- in top.py:
 - contains a simple module that has a 22bit counter that increments
on the main clock
 - the bottom 4 bits of the counter are exported to Pins C1 D2 D1 E2
 - top contains a submodule called 'ext_counter'
  - ext_counter contains a Signal called count, and top takes the MSB of ext.count
  and uses it to drive the user led.
- meanwhile, in ext_counter.py
 - ext_counter requests an external GPIO called ext_clock
 - ext_counter creates a new clock domain called 'ext'
 - ext_counter contains a Signal called count
 - ext_counter increments the Signal based on the clock domain called 'ext'
  - ie m.d.ext += ....
 - and then ... KEY INSIGHT ... we drive the clock of the ext clock domain by
 binding it to the 'ext_clock' resource in a comb statement.

By jumping a wire from C2 to one of the other pins, you can control the blink rate

## In other words.
top.py uses main clock to drive a counter. The LSBs of the counter will therefore
be clocking up at some divisor of the main clock (1, 2, 4, 8, 16 ...)
These LSBs are exposed on the external pins of the Teensy at C1 D2 D1 E2.
A jumper wire can connect those LSBs to C2, which is an input used by the
'ext_counter' submodule. The 'ext_counter' submodule creates a new clock domain
called 'ext' and uses the C2 input (called 'ext_clock') to drive the clock domain
and increment its own counter.
Back in top.py, the MSB of ext_counter's count is connected to the led, causing
it to flash.
By changing which of C1 D2 D1 E2 is jumped to C2, the blink rate of the led can
be controlled.

## What's next
- Put in a buffer between ext_counter and top - ie a string of 3 or so flip flops
- Experiment with driving the ext clock from something truly external to the system
