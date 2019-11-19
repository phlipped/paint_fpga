# What just happened
- successfully got a basic gpio-controllable blinky over in 'gpio_blinky' branch

# What happens next
- Create some skeleton files, i.e.
 - Custom platform definition that defines the necessary Resources of the entire
   project, and how they map to the GPIO (i.e. motor control outputs, limit
   switch inputs, SPI inputs/outputs)
 - Submodule for motor-controller combinatorial logic
 - Submodule for SPI
 - Primary module wires together SPI and combinatorial logic
- SPI
 - Experiment with different clock domains and clock domain crossing
- Design testing framework - need to work out how to do this. This should probably
  be done sooner rather than later
